
import time
import os
import signal
import click
import json
from typing import Union
from lib.cmds.utils import run_sync,run_async

def push_app(app_name: str, manifest: str="manifest.yml") -> None:
    click.echo("Pushing App to space")
    cwd = os.getcwd()
    os.chdir("./cf-app")
    cmd = ["cf", "push", app_name, '-f', manifest]
    code, result, status = run_sync(cmd)
    os.chdir(cwd)
    if code != 0:
        click.echo(status)
        raise click.ClickException(result)
    click.echo(status)
    click.echo("App Running\n")

def delete_app(app_name: str) -> None:
    click.echo("Deleting app to space")
    cmd = ["cf", "delete", '-f', app_name ]
    code, result, status = run_sync(cmd)
    if code != 0:
        click.echo(status)
        raise click.ClickException(result)
    click.echo(status)
    click.echo("App Deleted\n")

def enable_ssh(app_name: str) -> None:
    click.echo("Enabling SSH on App")
    cmd = ["cf", "enable-ssh", app_name ]
    code, result, status = run_sync(cmd)
    if code != 0:
        click.echo(status)
        raise click.ClickException(result)
    click.echo(status)
    click.echo("SSH enabled\n")

def create_service_key(key_name: str, service_name: str) -> None:
    click.echo("Creating Service Key...")
    cmd = ["cf", "create-service-key", service_name, key_name ]
    code, result, status = run_sync(cmd)
    if code != 0:
        click.echo(status)
        raise click.ClickException(result)
    click.echo(status)
    click.echo("Service Key Created\n")

def delete_service_key(key_name: str, service_name: str) -> None:
    click.echo("Deleting Service Key...")
    cmd = ["cf", "delete-service-key", "-f", service_name, key_name ]
    code, result, status = run_sync(cmd)
    if code != 0:
        click.echo(status)
        raise click.ClickException(result)
    click.echo(status)
    click.echo("Service Key Deleted\n")

def get_service_key(key_name: str, service_name: str) -> dict:
    click.echo("Retrieving Service Key...")
    cmd = ["cf", "service-key", service_name, key_name ]
    code, result, status = run_sync(cmd)
    if code != 0:
        click.echo(status)
        raise click.ClickException(result)
    click.echo(status)
    click.echo("Service Key Created.\n")
    cred_str = "\n".join(result.split("\n")[2:])
    return json.loads(cred_str)

def create_ssh_tunnel(app_name: str, src_port: int, dst_port: int, host: str) -> int:
    click.echo("Starting SSH Tunnel via App")
    click.echo("Processing... ", nl=False) 
    tunnel = f"{src_port}:{host}:{dst_port}"
    # cmd = ["cf", "ssh", app_name ,"-T","-L", tunnel ]
    cmd = f"cf ssh {app_name} -N -T -L {tunnel} &"
    proc = run_async(cmd, shell=True)
    time.sleep(5) # wait for tunnel to stabilize
    if proc.poll() == 0:
        click.secho("Command Succeeded!\n", fg='bright_green')
        click.echo(f"SSH Tunnel Running with PID {proc.pid+1}")
    else:
        click.secho("Command Failed!\n", fg='red')
        raise click.ClickException(proc.stderr.read())
    return proc.pid+1

def delete_ssh_tunnel(pid: int) -> None:
    click.echo(f"Closing SSH Tunnel with PID of {pid}")
    click.echo("Processing.... ", nl=False)
    os.kill(pid,signal.SIGKILL)
    click.secho("Command Succeeded!\n", fg='bright_green')
    click.echo(f"SSH Tunnel with PID of {pid} closed")