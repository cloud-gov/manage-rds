from typing import List
from lib.cmds.engine import Engine
from lib.cmds.utils import run_sync
from lib.cmds import cf_cmds as cf
import os.path as path
import tarfile
import click


class PgSql(Engine) :

    def is_pgcustom(self, file_name: str) -> bool:
        with open(file_name, "rb") as fd:
            head = fd.read(5)
            if head == b'PGDMP': return True
        return False

    def use_psql(self, file_name: str) -> bool:
        if path.isdir(file_name): return False
        if tarfile.is_tarfile(file_name): return False
        if self.is_pgcustom(file_name): return False
        return True

    def credentials(self, service_name: str, key_name: str='key') -> dict:
        cf.create_service_key(key_name, service_name )
        creds = cf.get_service_key(key_name, service_name)
        creds['local_port'] = int(creds.get("port"))+60000
        creds['uri'] = f"postgres://{creds['username']}:{creds['password']}@localhost:{creds['local_port']}/{creds['db_name']}"
        return creds

    def prerequisites(self) -> None:
        click.echo("Checking for locally installed postgres utilities")
        cmd = ["which", "psql"]
        code, result, status = run_sync(cmd)
        if code != 0:
            errstr = click.style("\npsql application is required but not found", fg='red')
            raise click.ClickException(errstr)
        click.echo(click.style("\npsql found!", fg='bright_green'))

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

    def backup(self, db_name: str, creds: dict, backup_file: str, options: str=None) -> None:
        click.echo(f"Backing up Postgres DB: {db_name}")
        if options is not None:
            opts = options.split()
        else:
            opts = list()

        cmd = [ "pg_dump", "-d", creds.get('uri'), "-f", backup_file]
        cmd.extend(opts)
        click.echo("Backing up with:")
        click.echo( click.style("\t"+" ".join(cmd), fg='yellow'))
        code, result, status = run_sync(cmd)
        if code != 0:
            click.echo(status)
            raise click.ClickException(result)
        click.echo(status)
        click.echo("Backup complete\n")

    def restore(self, db_name: str, creds: dict, backup_file: str, options: str=None) -> None:
        click.echo(f"Restoring to Postgres DB: {db_name}")
        if options is not None:
            opts = options.split()
        else:
            opts = list()
        if self.use_psql(backup_file):
            cmd = [ "psql" , "-d", creds.get('uri'),"-f", backup_file]
            cmd.extend(opts)
        else:
            cmd = [ "pg_restore" , "-d", creds.get('uri') ]
            cmd.extend(opts)
            cmd.append(backup_file)

        click.echo("Restoring with:")
        click.echo( click.style("\t"+" ".join(cmd), fg='yellow'))
        code, result, status = run_sync(cmd)
        if code != 0:
            click.echo(status)
            raise click.ClickException(result)
        click.echo(status)
        click.echo("Restore complete\n")    

    def default_options(self, options: str, ignore: bool=False) -> str:
        if ignore:
            return options
        opts = options.split()
        # should remove owner
        if not any( x in [ "-O","--no-owner"] for x in opts):
            opts.append("-O")
        # should remove objects before creating
        if not any( x in ["-c", "--clean"] for x in opts):
            opts.append("-c")
        # and use if-exists
        if "--if-exists" not in opts:
            opts.append("--if-exists")
        # dont create DB broker already did that
        if "-C" in opts:
            opts.remove("-C")

        return " ".join(opts)