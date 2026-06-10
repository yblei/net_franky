# 🤖 net_franky

**Use the [Franky library](https://github.com/TimSchneider42/franky) from non-realtime machines.**

[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Tests](https://github.com/yblei/net_franky/actions/workflows/scheduled-tests.yml/badge.svg)](https://github.com/yblei/net_franky/actions/workflows/scheduled-tests.yml)


## 🏗️ How it works

```
┌─────────────┐    RPyC     ┌─────────────┐    libfranka    ┌─────────────┐
│ Your Laptop │ ──────────► │ RT Server   │ ──────────────► │ Franka Robot│
│ (Or Cluster)│             │             │                 │             │
└─────────────┘             └─────────────┘                 └─────────────┘
```


## 🎯 Key Benefits:
- 🔌 **Drop-in replacement** for the franky library with function stubs
- ⚡ **Well proven** - building on the common rpyc library
- 🚀 **Simple** - 5 minutes to get started

---

## 🚀 Quick Start

We support several convenience functions to automatically manage your remote execution environment.
The following example will automatically ensure, your remote environment is accessible and setup.

- `autosetup=True` Automatically clones and installs net_franky on your remote machine.
- `autostart_remote_server=True` Ensures, the remote RPC server is running.
- `use_ssh_tunnel=True` Tunnels the connection to remote port 18812 through ssh in case your firewall direct port access on remote machiens.

Please follow [Manual Setup](##Manual-Setup) in case any of the above fails.

### Usage
```python
from net_franky import setup_net_franky
# Connect to remote server
setup_net_franky("server-ip", 18812, user="your_user", autosetup=True, autostart_remote_server=True, use_ssh_tunnel=True)

from net_franky.franky import Robot, CartesianMotion

robot = Robot("10.90.90.1")  # Replace this with your robot's IP

# Let's start slow (this lets the robot use a maximum of 5% of its velocity, acceleration, and jerk limits)
robot.relative_dynamics_factor = 0.05

# Move the robot 20cm along the relative X-axis of its end-effector
motion = CartesianMotion(Affine([0.2, 0.0, 0.0]), ReferenceType.Relative)
robot.move(motion)
```

## Manual Setup

### 1. Server Setup (Real-time machine)
```bash
# One-time setup
mkdir ~/net_franky && cd ~/net_franky
python -m venv .venv && source .venv/bin/activate
pip install net-franky[server]
```

### 2. Start server (Run in tmux/screen)
```bash
rpyc_classic -p 18812 --host 0.0.0.0
```

### 3. Installation

#### Install via `pip`
```bash
pip install net-franky
```

#### Install from source
```bash
git clone https://github.com/yblei/net_franky.git
cd net_franky
pip install -e .
```

**That's it!** 🎉 Your robot code now runs remotely.


---

## Deviation from franky: Wrapper around the robot class
Franky supports the registration of a callback function to a motion. 
This is useful to record trajectories or to stream pose information back for visualization. 
Since this function is called with 1000Hz and the calls are buffered, execution over the network leads to significant delays. 

We therefore provide a pointer to the latest motion callback data in 

```pyton
robot_state, time_step, rel_time, abs_time, control_signal = robot.get_last_callback_data()
```

**Warning:** If you get segmentation faults, make sure you use the same version of python on the server and the client.


## 🤝 Contributing

We welcome your contributions! Please feel free to report issues if there are any. If you have new ideas/features, please fork the repository, implement your changes, and create a pull request:)
