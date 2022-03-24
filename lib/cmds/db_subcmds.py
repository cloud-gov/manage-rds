from typing import List
from lib.cmds.utils import run_sync
import click
import time

def prereq_pgsql() -> None:
    click.echo("Checking for locally installed postgres utilities")
    cmd = ["which", "pg_dump"]
    code, result, status = run_sync(cmd)
    if code != 0:
        errstr = click.style("\npg_dump application is required but not found", fg='red')
        raise click.ClickException(errstr)
    click.echo(click.style("\npg_dump found!", fg='bright_green'))
    cmd = ["which", "pg_restore"]
    code, result, status = run_sync(cmd)
    if code != 0:
        errstr = click.style("\npg_restore application is required but not found", fg='red')
        raise click.ClickException(errstr)
    click.echo(click.style("\npg_restore found!", fg='bright_green'))

def backup_pgsql(db_name: str, creds: dict, backup_file: str, options: list=list()) -> None:
    click.echo(f"Backing up Postgres DB: {db_name}")
    cmd = [ "pg_dump", "-d",
        f"postgres://{creds['username']}:{creds['password']}@localhost:{creds['port']}/{creds['db_name']}",
        "-f", backup_file
    ]
    cmd.extend(options)
    click.echo("Backing up with:")
    click.echo( click.style("\t"+" ".join(cmd), fg='yellow'))
    code, result, status = run_sync(cmd)
    if code != 0:
        click.echo(status)
        raise click.ClickException(result)
    click.echo(status)
    click.echo("Backup complete\n")
    
def prereq_mysql() -> None:
    pass

def backup_mysql(db_name: str, creds: dict, backup_file: str) -> None:
    pass

def prereq_mssql() -> None:
    pass

def backup_mssql(db_name: str, creds: dict, backup_file: str) -> None:
    pass 