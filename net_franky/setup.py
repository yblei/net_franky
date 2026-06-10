import atexit
from dataclasses import dataclass
import select
import shlex
import socket
import socketserver
import sys
import threading
import time

@dataclass
class Config:
    IS_SETUP: bool = False
    IP: str | None = None
    PORT: int | None = None
    REMOTE_MANAGER: "RemoteFrankyManager | None" = None

cfg = Config()


class _ForwardServer(socketserver.ThreadingTCPServer):
    allow_reuse_address = True
    daemon_threads = True


class _ForwardHandler(socketserver.BaseRequestHandler):
    chain_host = None
    chain_port = None
    ssh_transport = None

    def handle(self):
        channel = self.ssh_transport.open_channel(
            "direct-tcpip",
            (self.chain_host, self.chain_port),
            self.request.getpeername(),
        )
        if channel is None:
            return
        try:
            while True:
                ready_to_read, _, _ = select.select([self.request, channel], [], [])
                if self.request in ready_to_read:
                    data = self.request.recv(1024)
                    if not data:
                        break
                    channel.sendall(data)
                if channel in ready_to_read:
                    data = channel.recv(1024)
                    if not data:
                        break
                    self.request.sendall(data)
        finally:
            channel.close()
            self.request.close()

def setup_net_franky(ip, port, autosetup=False, autostart_remote_server=False, use_ssh_tunnel=False, user = None, ssh_port = 22, netfranky_remote_path = "~/net_franky") -> None:
    cfg.IS_SETUP = True
    cfg.IP = ip
    cfg.PORT = port

    if autosetup:
        if user is None:
            raise ValueError("Remote user name 'user' attribute must be provided for automatic net_franky setup on the remote side autosetup.")

        rfm = RemoteFrankyManager(ip, port, user, ssh_port, netfranky_remote_path)
        if not rfm.check_franky_present():
            print("Remote net_franky setup not found.")
            while True:
                answer = input("Would you like to set up the remote net_franky? This will clone net_franky on the remote machine and install the required dependencies. (Y/n): ").strip().lower() or "y"
                if answer in ("y", "yes"):
                    rfm.run_remote_setup()
                    break
                elif answer in ("n", "no"):
                    break
                else:
                    print("Please enter 'Y' or 'N'.")

    if autostart_remote_server:
        if user is None:
            raise ValueError("Remote user name 'user' attribute must be provided for automatic net_franky setup on the remote side autostart_remote_server.")
        rfm = RemoteFrankyManager(ip, port, user, ssh_port, netfranky_remote_path)
        cfg.REMOTE_MANAGER = rfm
        print("Starting remote net_franky server...")
        try:
            rfm.run_remote_server()
        except RuntimeError as exc:
            if "Address already in use" not in str(exc):
                raise
            print(f"Remote net_franky server already appears to be running on {ip}:{port}. Reusing it.")
        if use_ssh_tunnel:
            rfm.wait_for_remote_port()
            cfg.IP, cfg.PORT = rfm.start_ssh_port_forward()
        rfm.wait_for_port(cfg.IP, cfg.PORT)


class RemoteFrankyManager:
    _remote_command_timeout = 5.0

    def __init__(self, ip, port, user, ssh_port, netfranky_remote_path):
        try:
            import paramiko
        except ModuleNotFoundError as exc:
            raise ModuleNotFoundError(
                "paramiko is required for remote setup support"
            ) from exc

        self.ip = ip
        self.port = port
        self.user = user
        self.ssh_port = ssh_port
        self.netfranky_remote_path = netfranky_remote_path
        self.remote_server_pid = None
        self.forward_host = None
        self.forward_port = None
        self._forward_server = None
        self._forward_thread = None
        self._remote_server_stdin = None
        self._remote_server_stdout = None
        self._remote_server_stderr = None
        self._cleanup_registered = False
        self.ssh_client = paramiko.SSHClient()
        self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.ssh_client.connect(hostname=self.ip, port=self.ssh_port, username=self.user, timeout=1)

    def _remote_shell_path(self):
        if self.netfranky_remote_path == "~":
            return '"$HOME"'
        if self.netfranky_remote_path.startswith("~/"):
            return f'"$HOME/{self.netfranky_remote_path[2:]}"'
        return shlex.quote(self.netfranky_remote_path)

    def check_franky_present(self):
        command = f"test -d {self._remote_shell_path()}"
        stdin, stdout, stderr = self.ssh_client.exec_command(command)
        exit_status = stdout.channel.recv_exit_status()
        error = stderr.read().decode().strip()
        if exit_status == 0:
            return True
        if error:
            raise RuntimeError(
                f"Unable to check remote setup at {self.netfranky_remote_path}: {error}"
            )
        return False

    def run_remote_setup(self):
        remote_path = self._remote_shell_path()
        command = (
            f"mkdir -p {remote_path} && "
            f"cd {remote_path} && "
            "python3 -m venv .venv && "
            ". .venv/bin/activate && "
            "pip install 'net-franky[server]'"
        )
        stdin, stdout, stderr = self.ssh_client.exec_command(command)
        exit_status = stdout.channel.recv_exit_status()
        output = stdout.read().decode()
        error = stderr.read().decode()
        if output:
            print(output, end="")
        if error:
            print(error, end="", file=sys.stderr)
        output = output.strip()
        error = error.strip()
        if exit_status != 0:
            raise RuntimeError(
                f"Remote setup failed at {self.netfranky_remote_path}: {error or output}"
            )
        print(f"Remote net_franky successfully installed to {self.netfranky_remote_path}.")
        return output
    
    def run_remote_server(self):
        remote_path = self._remote_shell_path()
        command = (
            f"cd {remote_path} && "
            f".venv/bin/rpyc_classic -p {self.port} --host 0.0.0.0"
        )
        stdin, stdout, stderr = self.ssh_client.exec_command(command)
        self._remote_server_stdin = stdin
        self._remote_server_stdout = stdout
        self._remote_server_stderr = stderr
        self._register_cleanup()
        return None

    def start_ssh_port_forward(self, local_host="127.0.0.1", local_port=0):
        if self._forward_server is not None:
            return self.forward_host, self.forward_port

        transport = self.ssh_client.get_transport()
        if transport is None or not transport.is_active():
            raise RuntimeError("SSH transport is not available for port forwarding")

        handler = type(
            "RemotePortForwardHandler",
            (_ForwardHandler,),
            {
                "chain_host": "127.0.0.1",
                "chain_port": self.port,
                "ssh_transport": transport,
            },
        )
        self._forward_server = _ForwardServer((local_host, local_port), handler)
        self._forward_thread = threading.Thread(
            target=self._forward_server.serve_forever,
            daemon=True,
        )
        self._forward_thread.start()
        self.forward_host, self.forward_port = self._forward_server.server_address
        self._register_cleanup()
        return self.forward_host, self.forward_port

    def wait_for_port(self, host, port, timeout=10.0):
        deadline = time.monotonic() + timeout
        last_error = None
        while time.monotonic() < deadline:
            try:
                with socket.create_connection((host, port), timeout=0.5):
                    return True
            except OSError as exc:
                last_error = exc
                time.sleep(0.2)
        raise RuntimeError(
            f"Timed out waiting for net_franky RPC server at {host}:{port}. Is the port reachable?"
        ) from last_error

    def wait_for_remote_port(self, timeout=10.0):
        deadline = time.monotonic() + timeout
        remote_check_script = (
            f'import socket; '
            f'sock = socket.create_connection(("127.0.0.1", {self.port}), timeout=0.5); '
            'sock.close()'
        )
        remote_check = (
            "python3 -c "
            f"{shlex.quote(remote_check_script)}"
        )
        last_error = None
        while time.monotonic() < deadline:
            stdin, stdout, stderr = self.ssh_client.exec_command(remote_check)
            exit_status = stdout.channel.recv_exit_status()
            if exit_status == 0:
                return True
            last_error = stderr.read().decode().strip() or stdout.read().decode().strip() or "remote port not ready"
            time.sleep(0.2)
        raise RuntimeError(
            f"Timed out waiting for remote net_franky RPC server at 127.0.0.1:{self.port}."
        ) from RuntimeError(last_error)

    def stop_remote_server(self):
        if self._remote_server_stdout is None and self._remote_server_stdin is None and self._remote_server_stderr is None:
            return False
        for stream_name in ("_remote_server_stdin", "_remote_server_stdout", "_remote_server_stderr"):
            stream = getattr(self, stream_name)
            if stream is None:
                continue
            try:
                stream.close()
            except Exception:
                pass
            setattr(self, stream_name, None)
        self.remote_server_pid = None
        return True

    def stop_ssh_port_forward(self):
        if self._forward_server is None:
            return False
        forward_server = self._forward_server
        forward_thread = self._forward_thread
        try:
            if (
                forward_thread is not None
                and forward_thread is not threading.current_thread()
                and getattr(forward_thread, "is_alive", lambda: True)()
            ):
                forward_server.shutdown()
            forward_server.server_close()
        finally:
            self._forward_server = None
            self._forward_thread = None
            self.forward_host = None
            self.forward_port = None
        return True

    def close(self):
        self.stop_ssh_port_forward()
        self.stop_remote_server()
        self.ssh_client.close()
        if cfg.REMOTE_MANAGER is self:
            cfg.REMOTE_MANAGER = None

    def _register_cleanup(self):
        if self._cleanup_registered:
            return
        atexit.register(self.close)
        self._cleanup_registered = True
