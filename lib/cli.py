import click
from lib import commands

CONTEXT_SETTINGS = dict(help_option_names=["-h", "-?", "--help"])


@click.group(context_settings=CONTEXT_SETTINGS)
def main():
    """
    Application to a backup, restore, or clone a rds service instance from the aws-broker
    """


## CHECK
@click.option(
    "-e",
    "--engine",
    type=click.Choice(["pgsql", "mysql", "mssql"], case_sensitive=False),
    default="pgsql",
    help="Database engine type",
    show_default=True,
)
@main.command(context_settings=CONTEXT_SETTINGS)
def check(engine):
    """
    Check local system for required utilities for a DB engine.
    """
    commands.check(engine)


## SETUP
@main.command(context_settings=CONTEXT_SETTINGS)
@click.option("-k", "--key", type=str, help="service key name", default="key")
@click.option("-a", "--app", type=str, help="app name", default="ssh-app")
@click.option(
    "-e",
    "--engine",
    type=click.Choice(["pgsql", "mysql", "mssql"], case_sensitive=False),
    default="pgsql",
    help="Database engine type",
    show_default=True,
)
@click.argument("service")
def setup(service, key, app, engine):
    """
    Setup app, key, and tunnel to a aws-rds service instance

    SERVICE name of the service instance
    """
    click.echo(f"Setting up key, app and tunnel for {service}")
    creds, _ = commands.setup(service, engine, app, key)
    click.echo(f"key, app and tunnel for {service} setup!")
    click.echo(f"You can connect to {service} with this uri:")
    click.secho(creds.get("uri"), fg="yellow")


## TEARDOWN
@main.command(context_settings=CONTEXT_SETTINGS)
@click.option("-k", "--key", type=str, help="service key name", default="key")
@click.option("-a", "--app", type=str, help="app name", default="ssh-app")
@click.option("-p", "--pid", type=int, help="pid of tunnel", default=0)
@click.argument("service")
def cleanup(
    service,
    pid,
    key,
    app,
):
    """
    Cleanup key, app, and tunnel to a aws-rds service instance

    SERVICE name of the db service instance
    """
    click.echo(f"Cleaning up the app, key and tunnel for {service}")
    commands.cleanup(service, pid, app, key)
    click.echo("Clean up complete")


## BACKUP
@main.command(context_settings=CONTEXT_SETTINGS)
@click.option(
    "-e",
    "--engine",
    type=click.Choice(["pgsql", "mysql", "mssql"], case_sensitive=False),
    default="pgsql",
    help="Database engine type",
    show_default=True,
)
@click.option(
    "-f",
    "--backup-file",
    default="db_backup.sql",
    help="Output file name",
    show_default=True,
)
@click.option(
    "-o",
    "--options",
    type=str,
    help="cli options for the backup client",
)
@click.option(
    "-s",
    "--setup",
    type=bool,
    default=True,
    help="peform app/tunnel setup",
    show_default=True,
)
@click.option(
    "-c",
    "--cleanup",
    type=bool,
    default=True,
    help="peform app/tunnel cleanup",
    show_default=True,
)
@click.option(
    "-k",
    "--key-name",
    type=str,
    default="key",
    help="use this service key name",
    show_default=True,
)
@click.option(
    "-a",
    "--app-name",
    type=str,
    default="ssh-app",
    help="use this app name",
    show_default=True,
)
@click.option(
    "--force-options",
    type=bool,
    default=False,
    help="override engine default options with yours",
    show_default=True,
)
@click.argument("source")
def backup(
    source,
    engine,
    backup_file,
    options,
    force_options,
    key_name,
    app_name,
    setup,
    cleanup,
):
    """
    Backup a SOURCE aws-rds service instance
    """
    click.echo(f"Backing up database: {source} to file: {backup_file}")
    commands.backup(
        source,
        engine,
        backup_file,
        options,
        force_options,
        service_key=key_name,
        app_name=app_name,
        do_setup=setup,
        do_teardown=cleanup,
    )


## RESTORE
@main.command(context_settings=CONTEXT_SETTINGS)
@click.option(
    "-e",
    "--engine",
    type=click.Choice(["pgsql", "mysql", "mssql"], case_sensitive=False),
    default="pgsql",
    help="Database engine type",
    show_default=True,
)
@click.option(
    "-f",
    "--backup-file",
    default="db_backup.sql",
    help="Output file name",
    show_default=True,
)
@click.option(
    "-o",
    "--options",
    type=str,
    help="cli options for the backup client",
)
@click.option(
    "-s",
    "--setup",
    type=bool,
    default=True,
    help="peform app/tunnel setup",
    show_default=True,
)
@click.option(
    "-c",
    "--cleanup",
    type=bool,
    default=True,
    help="peform app/tunnel teardown",
    show_default=True,
)
@click.option(
    "-k",
    "--key-name",
    type=str,
    default="key",
    help="use this service key name",
    show_default=True,
)
@click.option(
    "-a",
    "--app-name",
    type=str,
    default="ssh-app",
    help="use this app name",
    show_default=True,
)
@click.option(
    "--force-options",
    type=bool,
    default=False,
    help="override engine default options with yours",
    show_default=True,
)
@click.argument("destination")
def restore(
    destination,
    engine,
    backup_file,
    options,
    force_options,
    key_name,
    app_name,
    setup,
    cleanup,
):
    """
    Restore to a rds service instance from a backup file
    """
    click.echo(f"Restoring the database from file: {backup_file}")
    commands.restore(
        destination,
        engine,
        backup_file,
        options,
        force_options,
        service_key=key_name,
        app_name=app_name,
        do_setup=setup,
        do_cleanup=cleanup,
    )


## CLONE
@main.command(context_settings=CONTEXT_SETTINGS)
@click.option(
    "-e",
    "--engine",
    type=click.Choice(["pgsql", "mysql", "mssql"], case_sensitive=False),
    default="pgsql",
    help="Database engine type",
    show_default=True,
)
@click.option(
    "-f",
    "--backup-file",
    default="db_backup.sql",
    help="Output file name",
    show_default=True,
)
@click.option(
    "-b",
    "--boptions",
    type=str,
    help="cli options for the backup client",
)
@click.option(
    "-r",
    "--roptions",
    type=str,
    help="cli options for the restore client",
)
@click.option(
    "-k",
    "--key-name",
    type=str,
    default="key",
    help="use this service key name",
    show_default=True,
)
@click.option(
    "-a",
    "--app-name",
    type=str,
    default="ssh-app",
    help="use this app name",
    show_default=True,
)
@click.option(
    "--force-options",
    type=bool,
    default=False,
    help="override engine default options with yours",
    show_default=True,
)
@click.argument("source")
@click.argument("destination")
def clone(
    source,
    destination,
    engine,
    backup_file,
    boptions,
    roptions,
    force_options,
    key_name,
    app_name,
):
    """
    Migrate data from one rds service to another rds service instance
    """
    click.echo(f"Cloning the database: {source} to {destination}")
    commands.clone(
        source,
        destination,
        engine,
        backup_file,
        boptions,
        roptions,
        force_options,
        key_name,
        app_name,
    )
    click.echo("Cloning complete!")


if __name__ == "__main__":
    main()
