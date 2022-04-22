import click
from cg_manage_rds.cmds.utils import run_sync
from cg_manage_rds.cmds.engine import Engine
from cg_manage_rds.cmds import cf_cmds as cf


class MySql(Engine):
    def prerequisites(self) -> None:
        click.echo("Checking for locally installed mysql utilities")
        cmd = ["which", "mysql"]
        code, _, _ = run_sync(cmd)
        if code != 0:
            errstr = click.style(
                "\nmysql application is required but not found", fg="red"
            )
            raise click.ClickException(errstr)
        click.echo(click.style("\nmysql found!", fg="bright_green"))

        cmd = ["which", "mysqldump"]
        code, _, _ = run_sync(cmd)
        if code != 0:
            errstr = click.style(
                "\nmysqldump application is required but not found", fg="red"
            )
            raise click.ClickException(errstr)
        click.echo(click.style("\nmysqldump found!", fg="bright_green"))


    def export_svc(
        self, svc_name: str, creds: dict, backup_file: str, options: str="", ignore: bool = False
    ) -> None:
        click.echo(f"Exporting from MySql DB: {svc_name}")
        opts = self.default_export_options(options, ignore)
        # if options is not None:
        #     opts = options.split()
        # else:
        #     opts = list()
        base_opts = self._creds_to_opts(creds)
        cmd = ["mysqldump"]
        cmd.extend(base_opts)
        cmd.extend(opts)
        cmd.extend(["-r", backup_file, creds['db_name']])
        # mysqldump -u user -p"passwd" -h 127.0.0.1 -P 33306 -r backup_file -n --set-gtid-purged=OFF -f -y databasename
        click.echo("Exporting with:")
        click.echo(click.style("\t" + " ".join(cmd), fg="yellow"))
        code, result, status = run_sync(cmd)
        if code != 0:
            click.echo(status)
            raise click.ClickException(result)
        click.echo(status)
        click.echo("Export complete\n")

    def import_svc(
        self, svc_name: str, creds: dict, 
        backup_file: str, options: str= "", ignore: bool = False
    ) -> None:
        # mysql -u"user" -p"passwd" -h"127.0.0.1" -P"33306" -D"databasename" -e"source backup_file"
        click.echo(f"Importing to MySql DB: {svc_name}")
        opts = self.default_import_options(options,ignore)
        # if options is not None:
        #     opts = options.split()
        # else:
        #     opts = list()
        base_opts = self._creds_to_opts(creds)
        cmd = ["mysql"]
        cmd.extend(base_opts)
        cmd.extend(opts)
        cmd.extend([f"-D{creds['db_name']}", f"-e source {backup_file};"])
        click.echo("Importing with:")
        click.echo(click.style("\t" + " ".join(cmd), fg="yellow"))
        code, result, status = run_sync(cmd)
        if code != 0:
            click.echo(status)
            raise click.ClickException(result)
        click.echo(status)
        click.echo("Import complete\n")

    def credentials(self, service_name: str, key_name: str = "key") -> dict:
        cf.create_service_key(key_name, service_name)
        creds = cf.get_service_key(key_name, service_name)
        creds["local_port"] = int(creds.get("port")) + 30000
        creds['local_host'] = '127.0.0.1'
        creds['uri'] = f"mysql -u\"{creds['username']}\" -p\"{creds['password']}\" -h\"{creds['local_host']}\" -P\"{creds['local_port']}\" -D\"{creds['db_name']}\""
        return creds

    def default_export_options(self, options: str, ignore: bool = False) -> list:
        if options is not None:
            opts = options.split()
        else:
            opts = list()
        if ignore:
            return opts
        # dont create
        if not any(x in [ "-n", "--no-create-db"] for x in opts):
            opts.append("-n")
        # ignore tablespaces
        if not any(x in [ "-y", "--tablespaces" ] for x in opts):
            opts.append("-y")
        # push through errors
        if not any(x in [ "-f", "--force" ] for x in opts):
            opts.append("-f")
        if "--set-gtid-purged=OFF" not in opts:
            opts.append("--set-gtid-purged=OFF")
        if "--column-statistics=0" not in opts:
            opts.append("--column-statistics=0")
        return opts

    def default_import_options(self, options: str, ignore: bool = False) -> list:
        if options is not None:
            opts = options.split()
        else:
            opts = list()
        return opts

    def _creds_to_opts(self,creds: dict) -> list:
        opts = f"-u{creds['username']} "
        opts+=f"-p{creds['password']} "
        opts+=f"-P{creds['local_port']} "
        opts+=f"-h{creds['local_host']} "
        return opts.split()
