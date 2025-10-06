# iport dataclass
from dataclasses import dataclass
import subprocess
from telnetlib import IP
from contextlib import ExitStack
import atexit
import os
import signal
import time

@dataclass
class Config:
    IS_SETUP: bool = False
    IP: str | None = None
    PORT: int | None = None
    USER: str | None = None
    process: subprocess.Popen | None = None
    NETFRANKY_REMOTE_PATH: str | None = None

cfg = Config()

def setup_net_franky(ip, port, user = None, netfranky_remote_path = None) -> None:
    cfg.IS_SETUP = True
    cfg.IP = ip
    cfg.PORT = port
    cfg.USER = user
    cfg.NETFRANKY_REMOTE_PATH = netfranky_remote_path or "/home/" + user + "/net_franky"
    
def start_remote_server():
    import sys
    
    if not cfg.IS_SETUP:
        raise RuntimeError("net_franky is not set up. Please call setup_net_franky(ip, port, user) before starting the server.")
    if cfg.USER is None:
        raise RuntimeError("User is not set. Please provide a user when calling setup_net_franky(ip, port, user).")
    
    CLEANUPS = ExitStack()
    
    atexit.register(CLEANUPS.close)
    
    # check, if net_franky is present on the remote machine
    cmd_check = ["ssh", f"{cfg.USER}@{cfg.IP}", f"test -d {cfg.NETFRANKY_REMOTE_PATH} && echo 'exists' || echo 'not exists'"]
    result = subprocess.run(cmd_check, capture_output=True, text=True)
    if result.stdout.strip() != "exists":
        raise RuntimeError(f"net_franky is not present on the remote machine at {cfg.NETFRANKY_REMOTE_PATH}. Please clone the repository there.")
    
    # check, if the .venv is present on the remote machine
    cmd_check_venv = ["ssh", f"{cfg.USER}@{cfg.IP}", f"test -d {cfg.NETFRANKY_REMOTE_PATH}/.venv && echo 'exists' || echo 'not exists'"]
    result = subprocess.run(cmd_check_venv, capture_output=True, text=True)
    if result.stdout.strip() != "exists":
        raise RuntimeError(f"The .venv is not present on the remote machine at {cfg.NETFRANKY_REMOTE_PATH}/.venv. Please create a virtual environment there and install the required packages (see net_franky/README.md).")
    
    venv_python = f"{cfg.NETFRANKY_REMOTE_PATH}/.venv/bin/python3"

    # Fix: Use a list of arguments instead of a single string
    cmd = ["ssh", f"{cfg.USER}@{cfg.IP}", f"{venv_python} -m rpyc_classic -p {cfg.PORT}"]
    
    print(f"Starting remote RPyC server on {cfg.USER}@{cfg.IP}:{cfg.PORT}...")
    cfg.process = subprocess.Popen(
        cmd, 
        shell=False, 
        preexec_fn=os.setsid, 
        stdout=sys.stdout, 
        stderr=sys.stderr
    )
    time.sleep(2)  # Give the server a moment to start
    # check, if the process is running
    if cfg.process.poll() is None:
        print(f"Remote RPyC server started with PID {cfg.process.pid}.")
    else:
        raise RuntimeError("Failed to start remote RPyC server.")
    
    assert cfg.process is not None
    def cleanup():
        print("Cleaning up remote server...")
        os.killpg(cfg.process.pid, signal.SIGTERM)
    CLEANUPS.callback(cleanup)
