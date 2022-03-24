from typing import Tuple
from lib.cmds.cf_subcmds import *
from lib.cmds.db_subcmds import *
import click

def check_prerequisites(engine_type: str) -> None:
    if engine_type == "pgsql":
        prereq_pgsql()
    elif engine_type == "mysql":
        prereq_mysql()
    elif engine_type == 'mssql':
        prereq_mssql()
    else:
        raise click.ClickException(f"Unsupported Database Engine: {engine_type}")    

def setup(service_name: str, app_name: str='ssh-app', 
    key_name: str='key' ) -> Tuple[dict , int]:
    push_app(app_name)
    enable_ssh(app_name)
    create_service_key(key_name, service_name)
    creds = get_service_key(key_name, service_name)
    dst_port = int(creds.get("port"))
    src_port = dst_port+60000
    host = creds.get("host")
    pid = create_ssh_tunnel(app_name, src_port, dst_port, host)
    creds['host'] = "localhost"
    creds['port'] = src_port
    return (creds,pid)

def credentials(service_name: str, key_name: str='key') -> dict:
    creds = get_service_key(key_name, service_name)
    creds['host'] = "localhost"
    creds['port'] = int(creds.get("port"))+60000
    return creds

def cleanup(pid: int, service_name: str, 
    app_name: str='ssh-app', key_name: str='key' ) -> None:
    delete_ssh_tunnel(pid)
    delete_service_key(key_name, service_name)
    delete_app( app_name )

def backup_db(service_name: str, creds: dict,
     engine_type: str="pgsql", backup_file: str="db_backup.sql", options: str=""):
    if options is not None:
        opts = options.split()
    else:
        opts = list()

    if engine_type == "pgsql":
        backup_pgsql(service_name, creds, backup_file, opts)
    elif engine_type == "mysql":
        backup_mysql(service_name, creds, backup_file, opts)
    elif engine_type == 'mssql':
        backup_mssql(service_name, creds, backup_file, opts)
    else:
        raise click.ClickException(f"Unsupported Database Engine: {engine_type}")

def backup(service_name: str, engine_type: str="pgsql", 
    backup_file: str="db_backup.sql", options: str="",
    service_key: str="key", app_name: str="ssh-app",
    do_setup: bool=True, do_teardown: bool=True):

    click.echo("Checking Prerequisites for ")
    check_prerequisites(engine_type)
    click.echo("Prerequisites present\n")
    # either push app and create key, or reuse existing setup and key
    if do_setup:
        click.echo("Configuring CF space for SSH to Database")
        creds, pid = setup(service_name, app_name, service_key)
        click.echo("Config complete\n")
    else:
        click.echo("Retrieving credentials for Database") 
        creds = credentials(service_name, service_key)
        click.echo("Credentials ready\n") 

    click.echo("Performing backup")
    backup_db(service_name, creds, engine_type, backup_file, options)
    click.echo("Backup Completed\n")

    if do_teardown:
        click.echo("Removing config for SSH to Database")
        cleanup(pid, service_name)
        click.echo("Removal complete\n")

    click.echo(f"Backup file of database can be found in {backup_file}")

def restore() -> None:
    pass

def clone() -> None:
    pass