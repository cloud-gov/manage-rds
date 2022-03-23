from re import sub
import subprocess
import itertools,sys
from typing import Tuple

def run_sync(cmd: str ) -> Tuple[int, str, str]:
    spinner = itertools.cycle(['-', '/', '|', '\\'])
    OKGREEN = '\033[92m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    status=None
    result=None
    code=0
    with subprocess.Popen(cmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE, universal_newlines=True) as proc:
        sys.stdout.write( "Processing.... ")
        sys.stdout.flush()
        while proc.poll() is None:
            sys.stdout.write(next(spinner))   # write the next character
            sys.stdout.flush()                # flush stdout buffer (actual character display)
            sys.stdout.write('\b')            # erase the last written char
        sys.stdout.flush()
        code=proc.returncode
        if code != 0:
            status=f"{FAIL}Command Failed!{ENDC}"
            result=proc.stderr.read().strip()
        else:
            status=f"{OKGREEN}Command Succeeded!{ENDC}"
            result = proc.stdout.read().strip()
        return code, result, status

def run_async(cmd: str) -> subprocess.Popen:
    process= subprocess.Popen(cmd, stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL, )
    return process