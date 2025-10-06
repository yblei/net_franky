# 🤖 net_franky

**Use the [Franky library](https://github.com/TimSchneider42/franky) from non-realtime Machines.**

[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/status-alpha-orange.svg)]()


## 🏗️ How it works

```
┌─────────────┐    RPyC     ┌─────────────┐    libfranka    ┌─────────────┐
│ Your Laptop │ ──────────► │ RT Server   │ ──────────────► │ Franka Robot│
│             │             │             │                 │             │
└─────────────┘             └─────────────┘                 └─────────────┘
```


## 🎯 Key Benefits:
- 🔌 **Drop-in replacement** for the franky library with function stubs
- ⚡ **Well proven** - building on the common rpyc library
- 🚀 **Simple** - 5 minutes to get started

---

## 🚀 Quick Start

### 1. Server Setup (Real-time machine)
```bash
# One-time setup
mkdir ~/net_franky && cd ~/net_franky
python -m venv .venv && source .venv/bin/activate
pip install "net_franky[server] @ git+https://github.com/yblei/net_franky.git"
```

### 2. Start server (Run in tmux/screen)
```bash
rpyc_classic -p 18812
```

### 3. Client Usage (Your laptop)
```bash
pip install 'git+https://github.com/yblei/net_franky.git'
```

```python
from net_franky import setup_net_franky
from net_franky.franky import Robot

# Connect to remote server
setup_net_franky("server-ip", 18812)

# Use exactly like local franky
robot = Robot("192.168.1.100")
robot.move_to([0.3, 0.4, 0.5])
```

**That's it!** 🎉 Your robot code now runs remotely.


---

## 🤝 Contributing

We welcome contributions!
