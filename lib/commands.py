from typing import Tuple, Union
from lib.cmds import cf_cmds as cf
from lib.cmds.engine import Engine
from lib.cmds.pgsql import PgSql
from lib.cmds.mysql import MySql
from lib.cmds.mssql import MsSql
import click


def get_engine_handler(engine_type: str) -> Engine:
    if engine_type == "pgsql":
        return PgSql()
    elif engine_type == "mysql":
        return MySql()
    elif engine_type == 'mssql':
        return MsSql()
    else:
        raise click.ClickException(f"Unsupported Database Engine: {engine_type}")     

def check(engine_name: str="pgsql") -> None:
    engine = get_engine_handler(engine_name)
    engine.prerequisites()

def setup(service_name: str, engine: Union[Engine, str], app_name: str='ssh-app', 
    key_name: str='key' ) -> Tuple[dict , int]:
    if isinstance(engine, str):
        engine = get_engine_handler(engine)
    cf.push_app(app_name)
    cf.enable_ssh(app_name)
    creds = engine.credentials(service_name, key_name)
    local_port = creds.get('local_port')
    host = creds.get('host')
    remote_port = int(creds.get('port'))
    pid = cf.create_ssh_tunnel(app_name, local_port, remote_port, host)
    return (creds,pid)

def cleanup(service_name: str, pid: int=0, 
    app_name: str='ssh-app', key_name: str='key' ) -> None:
    if pid !=0:
        cf.delete_ssh_tunnel(pid)
    cf.delete_service_key(key_name, service_name)
    cf.delete_app( app_name )

def backup(service_name: str, engine_type: str="pgsql", 
    backup_file: str="db_backup.sql", options: str="", ignore_defaults: bool=False,
    service_key: str="key", app_name: str="ssh-app",
    do_setup: bool=True, do_teardown: bool=True) -> None:

    engine = get_engine_handler(engine_type)

    click.echo(f"Checking Prerequisites for {engine_type}")
    engine.prerequisites()
    click.echo("Prerequisites present\n")
    # either push app and create key, or reuse existing setup and key
    if do_setup:
        click.echo("Configuring CF space for SSH to Database")
        creds, pid = setup(service_name, engine, app_name, service_key)
        click.echo("Config complete\n")
    else:
        click.echo("Retrieving credentials for Database") 
        creds = engine.credentials(service_name, service_key)
        pid=0
        click.echo("Credentials ready\n") 

    click.echo("Performing backup")
    options = engine.default_options(options, ignore_defaults)
    engine.backup(service_name, creds, backup_file, options)
    #backup_db(service_name, creds, engine_type, backup_file, options)
    click.echo("Backup Completed\n")

    if do_teardown:
        click.echo("Removing config for SSH to Database")
        cleanup(service_name,pid)
        click.echo("Removal complete\n")

    click.echo(f"Backup file of database can be found in {backup_file}")

def restore(service_name: str, engine_type: str="pgsql", 
    backup_file: str="db_backup.sql", options: str="", ignore_defaults: bool=False,
    service_key: str="key", app_name: str="ssh-app",
    do_setup: bool=True, do_cleanup: bool=True) -> None:

    engine = get_engine_handler(engine_type)

    click.echo(f"Checking Prerequisites for {engine_type}")
    engine.prerequisites()
    click.echo("Prerequisites present\n")
    # either push app and create key, or reuse existing setup and key
    if do_setup:
        click.echo("Configuring CF space for SSH to Database")
        creds, pid = setup(service_name, engine, app_name, service_key)
        click.echo("Config complete\n")
    else:
        click.echo("Retrieving credentials for Database") 
        creds = engine.credentials(service_name, service_key)
        pid =0
        click.echo("Credentials ready\n") 

    click.echo("Performing Restoration")
    options = engine.default_options(options, ignore_defaults)
    engine.restore(service_name, creds, backup_file, options)
    click.echo("Restoration Completed\n")

    if do_cleanup:
        click.echo("Removing config for SSH to Database")
        cleanup(service_name,pid)
        click.echo("Removal complete\n")


def clone(src_service: str, dst_service: str, engine_type: str="pgsql", 
    backup_file: str="db_backup.sql", backup_options: str="",
    restore_options: str="", ignore_defaults: bool=False,
    service_key: str="key", app_name: str="ssh-app" ) -> None:
    
    engine = get_engine_handler(engine_type)

    click.echo(f"Checking Prerequisites for {engine_type}")
    engine.prerequisites()
    click.echo("Prerequisites present\n")

    # First Backup source
    click.echo(f"Setting up CF space for SSH to {src_service}")
    creds, pid = setup(src_service, engine, app_name, service_key)
    click.echo("Setup complete\n")

    click.echo(f"Performing backup of {src_service}")
    backup_options = engine.default_options(backup_options, ignore_defaults)
    engine.backup(src_service, creds, backup_file, backup_options)
    click.echo("Backup Completed\n")

    click.echo(f"Cleaning up SSH for {src_service}")
    cleanup(src_service, pid)
    click.echo("Cleanup complete\n")

    # Now restore to destination
    click.echo(f"Setting up CF space for SSH to {dst_service}")
    creds, pid = setup(dst_service, engine, app_name, service_key)
    click.echo("Setup complete\n")

    click.echo(f"Performing Restoration to {dst_service}")
    restore_options = engine.default_options(restore_options, ignore_defaults)
    engine.restore(dst_service, creds, backup_file, restore_options)
    click.echo("Restoration Completed\n")

    click.echo(f"Cleaning up SSH for {dst_service}")
    cleanup(dst_service, pid)
    click.echo("Cleanup complete\n")
