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

cfg = Config()

def setup_net_franky(ip, port, user = None, netfranky_remote_path = None) -> None:
    cfg.IS_SETUP = True
    cfg.IP = ip
    cfg.PORT = port
    

