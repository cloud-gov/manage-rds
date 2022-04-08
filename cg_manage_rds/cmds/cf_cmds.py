import time
import os
import sys
import signal
import click
import json
import re
import importlib.resources as ir
import cg_manage_rds
from cg_manage_rds.cmds.utils import run_sync, run_async


def push_app(app_name: str, manifest: str = "manifest.yml") -> None:
    click.echo("Pushing App to space")
    orig_wd=getattr(sys, "_MEIPASS", os.getcwd())
    app_dir = ir.files(cg_manage_rds).joinpath("cf-app").as_posix()
    #app_dir = os.path.join(base_path, "cf-app")
    os.chdir(app_dir)
    cmd = ["cf", "push", app_name, "-f", manifest]
    code, result, status = run_sync(cmd)
    os.chdir(orig_wd)
    if code != 0:
        click.echo(status)
        raise click.ClickException(result)
    click.echo(status)
    click.echo("App Running\n")


def delete_app(app_name: str) -> None:
    click.echo("Deleting app to space")
    cmd = ["cf", "delete", "-f", app_name]
    code, result, status = run_sync(cmd)
    if code != 0:
        click.echo(status)
        raise click.ClickException(result)
    click.echo(status)
    click.echo("App Deleted\n")


def enable_ssh(app_name: str) -> None:
    click.echo("Enabling SSH on App")
    cmd = ["cf", "enable-ssh", app_name]
    code, result, status = run_sync(cmd)
    if code != 0:
        click.echo(status)
        raise click.ClickException(result)
    click.echo(status)
    click.echo("SSH enabled\n")


def create_service_key(key_name: str, service_name: str) -> None:
    click.echo("Creating Service Key...")
    cmd = ["cf", "create-service-key", service_name, key_name]
    code, result, status = run_sync(cmd)
    if code != 0:
        click.echo(status)
        raise click.ClickException(result)
    click.echo(status)
    click.echo("Service Key Created\n")


def delete_service_key(key_name: str, service_name: str) -> None:
    click.echo("Deleting Service Key...")
    cmd = ["cf", "delete-service-key", "-f", service_name, key_name]
    code, result, status = run_sync(cmd)
    if code != 0:
        click.echo(status)
        raise click.ClickException(result)
    click.echo(status)
    click.echo("Service Key Deleted\n")


def get_service_key(key_name: str, service_name: str) -> dict:
    click.echo("Retrieving Service Key...")
    cmd = ["cf", "service-key", service_name, key_name]
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
    time.sleep(5)  # wait for tunnel to stabilize
    if proc.poll() == 0:
        click.secho("Command Succeeded!", fg="bright_green")
        click.echo(f"SSH Tunnel Running with PID {proc.pid+1}\n")
    else:
        click.secho("Command Failed!\n", fg="red")
        raise click.ClickException(proc.stderr.read())
    return proc.pid + 1


def delete_ssh_tunnel(pid: int) -> None:
    click.echo(f"Closing SSH Tunnel with PID of {pid}")
    click.echo("Processing.... ", nl=False)
    os.kill(pid, signal.SIGKILL)
    click.secho("Command Succeeded!", fg="bright_green")
    click.echo(f"SSH Tunnel with PID of {pid} closed\n")


def get_service_plan(service: str) -> str:
    click.echo("Retrieving Service Info...")
    cmd = ["cf", "service", service]
    code, result, status = run_sync(cmd)
    planmatch = re.search("plan:.*\n",result)
    if code != 0 or planmatch is None:
        click.echo(status)
        raise click.ClickException(result)
    planline = planmatch.group()
    return planline.split()[-1]
