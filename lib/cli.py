import click
from lib.backup import do_backup


@click.group()
def main():
    """
        Application to a backup, restore, or clone a rds service instance from the aws-broker
    """
    pass

## BACKUP
@main.command()
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
@click.argument("src")
def backup(src, engine, backup_file, options, setup, teardown):
    """
        Backup from a rds service instance to a backup file
    """
    click.echo(f"Backing up database: {src} to file: {backup_file}")
    do_backup(src, engine, backup_file, options, setup, teardown)

## RESTORE
@main.command()
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
@click.argument("src")
def restore(src, engine, backup_file):
    """
        Restore to a rds service instance from a backup file
    """
    click.echo('Restoring the database')


## CLONE
@main.command()
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
@click.argument("src")
@click.argument("dest")
def clone(src, dest, engine, backup_file):
    """
        Migrate data from one rds service to another rds service instance
    """
    click.echo(f"Cloning the database: {src} to {dest}")

if __name__ == '__main__':
    main()