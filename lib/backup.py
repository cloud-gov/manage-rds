from multiprocessing.connection import wait
from lib.common import *
import click


def do_backup(db_name: str, engine_type: str="pgsql", 
    backup_file: str="db_backup.sql", options: str="",
    do_setup: bool=True, do_teardown: bool=True):

    click.echo("Checking Prerequisites for ")
    check_prerequisites(engine_type)
    click.echo("Prerequisites present")

    if do_setup:
        click.echo("Configuring CF space for SSH to Database")
        creds, tunnel = setup(db_name)
        click.echo("Config complete")
    else:
        creds = credentials(db_name)

    click.echo("Performing backup")
    backup_db(db_name, creds, engine_type, backup_file, options)
    click.echo("Backup Completed")

    if do_teardown:
        click.echo("Removing config for SSH to Database")
        teardown(tunnel, db_name)
        click.echo("Removal complete")

    click.echo(f"Backup file of database can be found in {backup_file}")