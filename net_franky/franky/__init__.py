import sys
import rpyc

from net_franky.setup import cfg

err_msg = (
    "net_franky is not set up. Please call setup_net_franky(ip, port) before importing franky. See README.md for details."
)
if not cfg.IS_SETUP:
    raise RuntimeError(err_msg)

# Get reference to current module
current_module = sys.modules[__name__]

try:
    conn = rpyc.classic.connect(cfg.IP, cfg.PORT)
except ConnectionRefusedError as e:
    raise ConnectionRefusedError(
        f"Could not connect to remote server at {cfg.IP}:{cfg.PORT}. "
        "Make sure the remote server is running and accessible."
    ) from e

franky = conn.modules["franky"]
cb_robot = conn.modules["net_franky.cb_robot"]

# Add all remote franky attributes to current module
for attr_name in dir(franky):
    if attr_name == "Robot":
        # we use our own robot class that wraps franky.Robot. It only adds callback functionality to buffer the latest robot state.
        setattr(current_module, "Robot", cb_robot.CBRobot)
        continue
    if not attr_name.startswith('_'):
        setattr(current_module, attr_name, getattr(franky, attr_name))