
from subprocess import Popen
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
    key_name: str='key' ) -> Tuple[dict , subprocess.Popen]:

    push_app(app_name)
 
    enable_ssh(app_name)

    create_service_key(key_name, service_name)

    creds = get_service_key(key_name, service_name)

    dst_port = int(creds.get("port"))
    src_port = dst_port+60000
    host = creds.get("host")
    tunnel = create_ssh_tunnel(app_name, src_port, dst_port, host)
    creds['host'] = "localhost"
    creds['port'] = src_port
    return (creds,tunnel)

def credentials(service_name: str, key_name: str='key') -> dict:
    creds = get_service_key(key_name, service_name)
    return creds

def teardown(tunnel: subprocess.Popen, service_name: str, 
    app_name: str='ssh-app', key_name: str='key' ) -> None:

    delete_ssh_tunnel(tunnel)

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
