from typing import Any
import rpyc
from rpyc import Service
from rpyc.utils.classic import obtain
from franky import *
from rpyc.core import brine

config = {
    'allow_all_attrs': True,
    'allow_pickle': True,
    'allow_getattr': True,
    'allow_setattr': True,
    'allow_delattr': True,
    'sync_request_timeout': 100,
}
        
class NetRobotServer(Service):
    def __init__(self):
        self.robot = Robot("192.168.100.1")

class NetRobot(Service):
    def __init__(self):
        self.client = rpyc.connect("localhost", 18861, config=config)
        self.robot = self.client.root.robot
        
    def __getattr__(self, name: str) -> Any:
        """
        Delegate attribute access to the underlying Robot instance.
        If the attribute is callable, wrap it to ensure that any Net* classes
        in the arguments are converted to their corresponding franky classes.
        """
        # if it is an attribute of the Robot instance, return it
        # potentially we need to obtain it later ...
        attr = getattr(self.robot, name)
        
        # if it is a callable, we need to run it on the server side
        if callable(attr):
            def wrapper(*args, **kwargs):
                return attr(*args, **kwargs)
            return wrapper
        return attr

if __name__ == "__main__":
    from rpyc.utils.server import ThreadedServer
    
    
    # Start RPyC server
    server = ThreadedServer(NetRobotServer, port=18861, protocol_config=config)
    print("Starting RPyC server on port 18861...")
    server.start()