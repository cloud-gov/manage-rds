from typing import Tuple
import click
import re
from cg_manage_rds.cmds import cf_cmds as cf
from cg_manage_rds.cmds.engine import Engine
from cg_manage_rds.cmds.pgsql import PgSql
from cg_manage_rds.cmds.mysql import MySql

def find_engine_type(service_name: str)->str:
    cf.check_cf_cli()
    plan=cf.get_service_plan(service_name)
    if re.search("mysql", plan):
        return 'mysql'
    if re.search("psql", plan):
        return "pgsql"
    raise click.ClickException(f"Unsported service plan: {plan}")

def get_engine_handler(engine_type: str) -> Engine:
    if engine_type == "pgsql":
        return PgSql()
    elif engine_type == "mysql":
        return MySql()
    else:
        raise click.ClickException(f"Unsupported Database Engine: {engine_type}")


def check(service: str, engine_name: str=None) -> None:
    if engine_name is None:
        engine_name = find_engine_type(service)
    engine = get_engine_handler(engine_name)
    engine.prerequisites()

def setup(
    service_name: str,
    engine_type: str = None,
    app_name: str = "ssh-app",
    key_name: str = "key",
    engine: Engine= None,
) -> Tuple[dict, int]:

    if engine_type is None:
        engine_type = find_engine_type(service_name)

    if engine is None:
        engine = get_engine_handler(engine_type)

    cf.push_app(app_name)
    cf.enable_ssh(app_name)
    creds = engine.credentials(service_name, key_name)
    local_port = int(creds.get("local_port"))
    host = creds.get("host")
    remote_port = int(creds.get("port"))
    pid = cf.create_ssh_tunnel(app_name, local_port, remote_port, host)
    return (creds, pid)


def cleanup(
    service_name: str, pid: int = 0, app_name: str = "ssh-app", key_name: str = "key"
) -> None:
    cf.check_cf_cli()
    if pid != 0:
        cf.delete_ssh_tunnel(pid)
    cf.delete_service_key(key_name, service_name)
    cf.delete_app(app_name)


def export_from_svc(
    service_name: str,
    engine_type: str = None,
    backup_file: str = "db_backup.sql",
    options: str = "",
    ignore_defaults: bool = False,
    service_key: str = "key",
    app_name: str = "ssh-app",
    do_setup: bool = True,
    do_teardown: bool = True,
) -> None:

    if engine_type is None:
        engine_type = find_engine_type(service_name)

    engine = get_engine_handler(engine_type)

    click.echo(f"Checking Prerequisites for {engine_type}")
    engine.prerequisites()
    click.echo("Prerequisites present\n")
    # either push app and create key, or reuse existing setup and key
    if do_setup:
        click.echo("Configuring CF space for SSH to Service")
        creds, pid = setup(service_name, app_name=app_name, key_name=service_key, engine=engine)
        click.echo("Config complete\n")
    else:
        click.echo("Retrieving credentials for Service")
        creds = engine.credentials(service_name, service_key)
        pid = 0
        click.echo("Credentials ready\n")

    click.echo("Performing export")
    engine.export_svc(service_name, creds, backup_file, options, ignore_defaults)
    # backup_db(service_name, creds, engine_type, backup_file, options)
    click.echo("Export completed\n")

    if do_teardown:
        click.echo("Removing config for SSH to Database")
        cleanup(service_name, pid)
        click.echo("Removal complete\n")

    click.echo(f"Export file of {service_name} can be found in {backup_file}")


def import_to_svc(
    service_name: str,
    engine_type: str = None,
    backup_file: str = "db_backup.sql",
    options: str = "",
    ignore_defaults: bool = False,
    service_key: str = "key",
    app_name: str = "ssh-app",
    do_setup: bool = True,
    do_cleanup: bool = True,
) -> None:

    if engine_type is None:
        engine_type = find_engine_type(service_name)

    engine = get_engine_handler(engine_type)

    click.echo(f"Checking Prerequisites for {engine_type}")
    engine.prerequisites()
    click.echo("Prerequisites present\n")
    # either push app and create key, or reuse existing setup and key
    if do_setup:
        click.echo("Configuring CF space for SSH to Database")
        creds, pid = setup(service_name, app_name=app_name, key_name=service_key, engine=engine)
        click.echo("Config complete\n")
    else:
        click.echo("Retrieving credentials for Database")
        creds = engine.credentials(service_name, service_key)
        pid = 0
        click.echo("Credentials ready\n")

    click.echo("Performing import")
    engine.import_svc(service_name, creds, backup_file, options, ignore_defaults)
    click.echo("Import completed\n")

    if do_cleanup:
        click.echo("Removing config for SSH to Database")
        cleanup(service_name, pid)
        click.echo("Removal complete\n")


def clone(
    src_service: str,
    dst_service: str,
    engine_type: str = None,
    backup_file: str = "db_backup.sql",
    backup_options: str = "",
    restore_options: str = "",
    ignore_defaults: bool = False,
    service_key: str = "key",
    app_name: str = "ssh-app",
) -> None:

    if engine_type is None:
        engine_type = find_engine_type(src_service)

    engine = get_engine_handler(engine_type)

    click.echo(f"Checking Prerequisites for {engine_type}")
    engine.prerequisites()
    click.echo("Prerequisites present\n")

    # First Backup source
    click.echo(f"Setting up CF space for SSH to {src_service}")
    creds, pid = setup(src_service, app_name=app_name, key_name=service_key, engine=engine)
    click.echo("Setup complete\n")

    click.echo(f"Performing exprot of {src_service}")
    engine.export_svc(src_service, creds, backup_file, backup_options, ignore_defaults)
    click.echo("Export completed\n")

    click.echo(f"Cleaning up SSH for {src_service}")
    cleanup(src_service, pid)
    click.echo("Cleanup complete\n")

    # Now restore to destination
    click.echo(f"Setting up CF space for SSH to {dst_service}")
    creds, pid = setup(dst_service, app_name=app_name, key_name=service_key, engine=engine)
    click.echo("Setup complete\n")

    click.echo(f"Performing import to {dst_service}")
    engine.import_svc(dst_service, creds, backup_file, restore_options, ignore_defaults)
    click.echo("Import Completed\n")

    click.echo(f"Cleaning up SSH for {dst_service}")
    cleanup(dst_service, pid)
    click.echo("Cleanup complete\n")
