import subprocess
import os
import click
import json
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

def create_ssh_tunnel(app_name: str, src_port: int, dst_port: int, host: str) -> subprocess.Popen:
    click.echo("Starting SSH Tunnel via App")
    tunnel = f"{src_port}:{host}:{dst_port}"
    cmd = ["cf", "ssh", "-L", tunnel , app_name ]
    proc = run_async(cmd)
    if proc.poll() == None:
        click.echo(f"SSH Tunnel Running with PID {proc.pid}")
        click.echo(click.style("Command Succeeded!\n", fg='green'))
    else:
        click.echo(click.style("Command Failed!\n", fg='red'))
        raise click.ClickException(proc.stderr.read())
    return proc

def delete_ssh_tunnel(process: subprocess.Popen) -> None:
    click.echo(f"Closing SSH Tunnel with PID of {process.pid}")
    process.kill()
    code=process.poll()
    click.echo(f"SSH Tunnel closed with Code: {code}") 
    click.echo(click.style("Command Succeeded!\n", fg='green'))