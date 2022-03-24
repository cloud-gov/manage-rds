
import click
from lib import commands

CONTEXT_SETTINGS = dict(help_option_names=['-h', '-?','--help'])

@click.group(context_settings=CONTEXT_SETTINGS)
def main():
    """
        Application to a backup, restore, or clone a rds service instance from the aws-broker
    """
    pass

## SETUP
@main.command(context_settings=CONTEXT_SETTINGS)
@click.option("-k","--key",
    type=str,
    help="service key name",
    default='key'
)
@click.option("-a","--app",
    type=str,
    help="app name",
    default='ssh-app'
)
@click.argument("service")
def setup(service, key, app):
    """
        Setup app, key, and tunnel to a aws-rds service instance

        SERVICE name of the service instance
    """
    click.echo(f'Setting up key, app and tunnel for {service}')
    commands.setup(service, app, key)
    click.echo(f'key, app and tunnel for {service} setup!')


## TEARDOWN
@main.command(context_settings=CONTEXT_SETTINGS)
@click.option("-k","--key",
    type=str,
    help="service key name",
    default='key'
)
@click.option("-a","--app",
    type=str,
    help="app name",
    default='ssh-app'
)
@click.argument("pid")
@click.argument("service")
def cleanup(pid,service, key, app, ):
    """
        Cleanup key, app, and tunnel to a aws-rds service instance

        \b
        PID of the running ssh tunnel
        SERVICE name of the db service instance  
    """
    click.echo(f'Cleaning up the app, key and tunnel for {service}')
    commands.cleanup(int(pid),service,app, key)
    click.echo(f'Clean up complete')

## BACKUP
@main.command(context_settings=CONTEXT_SETTINGS)
@click.option("-e","--engine", 
    type=click.Choice(['pgsql','mysql','mssql'],
    case_sensitive=False),
    default="pgsql", 
    help="Database engine type",
    show_default=True
)
@click.option("-b","--backup-file", 
    default="db_backup.sql", 
    help="Output file name",
    show_default=True
)
@click.option("-o","--options",
    type=str,
    help="cli options for the backup client",
)
@click.option("-s","--setup",
    type=bool, default=True,
    help="peform app/tunnel setup",
    show_default=True
)
@click.option("-t","--teardown",
    type=bool, default=True,
    help="peform app/tunnel teardown",
    show_default=True
)
@click.argument("source")
def backup(source, engine, backup_file, options, setup, teardown):
    """
        Backup a SOURCE aws-rds service instance 
    """
    click.echo(f"Backing up database: {source} to file: {backup_file}")
    commands.backup(source, engine, backup_file, options, do_setup=setup, do_teardown=teardown)

## RESTORE
@main.command(context_settings=CONTEXT_SETTINGS)
@click.option("-e","--engine", 
    type=click.Choice(['pgsql','mysql','mssql'],
    case_sensitive=False),
    default="pgsql", 
    help="Database engine type, default: pgsql"
)
@click.option("-b","--backup-file", 
    default="db_backup.sql", 
    help="Database backup file name, default: db_backup.sql"
)
@click.argument("source")
def restore(source, engine, backup_file):
    """
        Restore to a rds service instance from a backup file
    """
    click.echo('Restoring the database')
    commands.restore()

## CLONE
@main.command(context_settings=CONTEXT_SETTINGS)
@click.option("-e","--engine", 
    type=click.Choice(['pgsql','mysql','mssql'],
    case_sensitive=False),
    default="pgsql", 
    help="Database engine type, default: pgsql"
)
@click.option("-b","--backup-file", 
    default="db_backup.sql", 
    help="Database backup file name, default: db_backup.sql"
)
@click.argument("source")
@click.argument("dest")
def clone(source, dest, engine, backup_file):
    """
        Migrate data from one rds service to another rds service instance
    """
    click.echo(f"Cloning the database: {source} to {dest}")
    commands.clone()


if __name__ == '__main__':
    main()