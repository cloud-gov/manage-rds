from os import path
import tarfile
import click

from cg_manage_rds.cmds.engine import Engine
from cg_manage_rds.cmds.utils import run_sync
from cg_manage_rds.cmds import cf_cmds as cf


class PgSql(Engine):

    def credentials(self, service_name: str, key_name: str = "key") -> dict:
        cf.create_service_key(key_name, service_name)
        creds = cf.get_service_key(key_name, service_name)
        creds["local_port"] = int(creds.get("port")) + 60000
        creds["uri"] = (
            f"postgres://{creds['username']}:{creds['password']}@localhost:{creds['local_port']}/{creds['db_name']}"
        )
        return creds

    def prerequisites(self) -> None:
        cf.check_cf_cli()
        click.echo("Checking for locally installed postgres utilities")
        cmd = ["which", "psql"]
        code, _, _ = run_sync(cmd)
        if code != 0:
            errstr = click.style(
                "\npsql application is required but not found", fg="red"
            )
            raise click.ClickException(errstr)
        click.echo(click.style("\npsql found!", fg="bright_green"))

        cmd = ["which", "pg_dump"]
        code, _, _ = run_sync(cmd)
        if code != 0:
            errstr = click.style(
                "\npg_dump application is required but not found", fg="red"
            )
            raise click.ClickException(errstr)
        click.echo(click.style("\npg_dump found!", fg="bright_green"))

        cmd = ["which", "pg_restore"]
        code, _, _ = run_sync(cmd)
        if code != 0:
            errstr = click.style(
                "\npg_restore application is required but not found", fg="red"
            )
            raise click.ClickException(errstr)
        click.echo(click.style("\npg_restore found!", fg="bright_green"))

    def export_svc(
        self,
        svc_name: str,
        creds: dict,
        backup_file: str,
        options: str = None,
        ignore: bool = False,
    ) -> None:
        click.echo(f"Exporting Postgres DB: {svc_name}")
        if options is not None:
            opts = options.split()
        else:
            opts = list()
        opts = self.default_export_options(options, ignore)
        cmd = ["pg_dump", "-d", creds.get("uri"), "-f", backup_file]
        cmd.extend(opts)
        click.echo("Exporting up with:")
        click.echo(click.style("\t" + " ".join(cmd), fg="yellow"))
        code, result, status = run_sync(cmd)
        if code != 0:
            click.echo(status)
            raise click.ClickException(result)
        click.echo(status)
        click.echo("Export complete\n")

    def import_svc(
        self,
        svc_name: str,
        creds: dict,
        backup_file: str,
        options: str = None,
        ignore: bool = False,
    ) -> None:
        click.echo(f"Importing to Postgres DB: {svc_name}")
        if options is not None:
            opts = options.split()
        else:
            opts = list()
        if self._use_psql(backup_file):  # sql file
            cmd = ["psql", "-d", creds.get("uri"), "-f", backup_file]
            cmd.extend(opts)
        else:  # non sql format
            cmd = ["pg_restore", "-d", creds.get("uri")]
            opts = self.default_import_options(options, ignore)
            cmd.extend(opts)
            cmd.append(backup_file)

        click.echo("Importing with:")
        click.echo(click.style("\t" + " ".join(cmd), fg="yellow"))
        code, result, status = run_sync(cmd)
        if code != 0:
            click.echo(status)
            raise click.ClickException(result)
        click.echo(status)
        click.echo("Import complete\n")

    def default_export_options(self, options: str, ignore: bool = False) -> list:
        return self._default_options(options, ignore)

    def default_import_options(self, options: str, ignore: bool = False) -> list:
        return self._default_options(options, ignore)

    def _default_options(self, options: str, ignore: bool = False) -> list:
        if options is not None:
            opts = options.split()
        else:
            opts = list()
        if ignore:
            return opts
        # should remove owner
        if not any(x in ["-O", "--no-owner"] for x in opts):
            opts.append("-O")
        # should remove objects before creating
        if not any(x in ["-c", "--clean"] for x in opts):
            opts.append("-c")
        # and use if-exists
        if "--if-exists" not in opts:
            opts.append("--if-exists")
        # dont create DB broker already did that
        if "-C" in opts:
            opts.remove("-C")
        return opts

    def _is_pgcustom(self, file_name: str) -> bool:
        with open(file_name, "rb") as fd:
            head = fd.read(5)
            if head == b"PGDMP":
                return True
        return False

    def _use_psql(self, file_name: str) -> bool:
        if path.isdir(file_name):
            return False
        if tarfile.is_tarfile(file_name):
            return False
        if self._is_pgcustom(file_name):
            return False
        return True
