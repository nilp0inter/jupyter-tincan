from pathlib import Path
import argparse
import json
import signal
import socket
import subprocess
import sys

import zmq
from tornado import ioloop
from zmq.eventloop.zmqstream import ZMQStream


class JupyterKernelProxy:
    def __init__(self, ip, frontend_ports, kernel_ports, inner_kernel_process):
        self.context = zmq.Context()
        self.ip = ip
        self.frontend_ports = frontend_ports
        self.kernel_ports = kernel_ports
        self.inner_kernel_process = inner_kernel_process
        self._setup_proxy_sockets()
        self._setup_proxy_streams()

    def _setup_proxy_sockets(self):
        # Shell and Control use ROUTER for frontend, DEALER for backend
        self.shell_socket = self.context.socket(zmq.ROUTER)
        self.control_socket = self.context.socket(zmq.ROUTER)
        self.kernel_shell_socket = self.context.socket(zmq.DEALER)
        self.kernel_control_socket = self.context.socket(zmq.DEALER)

        # IOPub uses SUB for kernel, PUB for frontend
        self.iopub_socket = self.context.socket(zmq.PUB)
        self.kernel_iopub_socket = self.context.socket(zmq.SUB)
        self.kernel_iopub_socket.setsockopt(zmq.SUBSCRIBE, b'')

        # Stdin uses ROUTER for frontend, DEALER for backend
        self.stdin_socket = self.context.socket(zmq.ROUTER)
        self.kernel_stdin_socket = self.context.socket(zmq.DEALER)

        # Heartbeat uses PAIR on both ends
        self.hb_socket = self.context.socket(zmq.PAIR)
        self.kernel_hb_socket = self.context.socket(zmq.PAIR)

        # Bind frontend sockets
        self.shell_socket.bind(f"tcp://{self.ip}:{self.frontend_ports['shell_port']}")
        self.iopub_socket.bind(f"tcp://{self.ip}:{self.frontend_ports['iopub_port']}")
        self.stdin_socket.bind(f"tcp://{self.ip}:{self.frontend_ports['stdin_port']}")
        self.control_socket.bind(f"tcp://{self.ip}:{self.frontend_ports['control_port']}")
        self.hb_socket.bind(f"tcp://{self.ip}:{self.frontend_ports['hb_port']}")

        # Connect to the actual kernel sockets
        self.kernel_shell_socket.connect(f"tcp://{self.ip}:{self.kernel_ports['shell_port']}")
        self.kernel_iopub_socket.connect(f"tcp://{self.ip}:{self.kernel_ports['iopub_port']}")
        self.kernel_stdin_socket.connect(f"tcp://{self.ip}:{self.kernel_ports['stdin_port']}")
        self.kernel_control_socket.connect(f"tcp://{self.ip}:{self.kernel_ports['control_port']}")
        self.kernel_hb_socket.connect(f"tcp://{self.ip}:{self.kernel_ports['hb_port']}")

    def _setup_proxy_streams(self):
        self.shell_stream = ZMQStream(self.shell_socket)
        self.control_stream = ZMQStream(self.control_socket)
        self.stdin_stream = ZMQStream(self.stdin_socket)
        self.iopub_stream = ZMQStream(self.iopub_socket)
        self.hb_stream = ZMQStream(self.hb_socket)

        self.shell_stream.on_recv(self._forward_to_kernel_shell)
        self.control_stream.on_recv(self._forward_to_kernel_control)
        self.stdin_stream.on_recv(self._forward_to_kernel_stdin)
        self.iopub_stream.on_recv(self._forward_to_kernel_iopub)
        self.hb_stream.on_recv(self._forward_to_kernel_hb)

        self.kernel_shell_stream = ZMQStream(self.kernel_shell_socket)
        self.kernel_control_stream = ZMQStream(self.kernel_control_socket)
        self.kernel_stdin_stream = ZMQStream(self.kernel_stdin_socket)
        self.kernel_iopub_stream = ZMQStream(self.kernel_iopub_socket)
        self.kernel_hb_stream = ZMQStream(self.kernel_hb_socket)

        self.kernel_shell_stream.on_recv(self._forward_to_frontend_shell)
        self.kernel_control_stream.on_recv(self._forward_to_frontend_control)
        self.kernel_stdin_stream.on_recv(self._forward_to_frontend_stdin)
        self.kernel_iopub_stream.on_recv(self._forward_to_frontend_iopub)
        self.kernel_hb_stream.on_recv(self._forward_to_frontend_hb)

    def _forward_to_kernel_shell(self, msg):
        print(f"F>P>K (Shell) {msg}")
        self.kernel_shell_stream.send_multipart(msg)

    def _forward_to_kernel_control(self, msg):
        print(f"F>P>K (Control) {msg}")
        self.kernel_control_stream.send_multipart(msg)

    def _forward_to_kernel_stdin(self, msg):
        print(f"F>P>K (Stdin) {msg}")
        self.kernel_stdin_stream.send_multipart(msg)

    def _forward_to_kernel_iopub(self, msg):
        # print(f"F>P>K (IOPub) {msg}")
        self.kernel_iopub_stream.send_multipart(msg)

    def _forward_to_kernel_hb(self, msg):
        print(f"F>P>K (HB) {msg}")
        self.kernel_hb_stream.send_multipart(msg)

    def _forward_to_frontend_shell(self, msg):
        print(f"F<P<K (Shell) {msg}")
        self.shell_stream.send_multipart(msg)

    def _forward_to_frontend_control(self, msg):
        print(f"F<P<K (Control) {msg}")
        self.control_stream.send_multipart(msg)

    def _forward_to_frontend_stdin(self, msg):
        print(f"F<P<K (Stdin) {msg}")
        self.stdin_stream.send_multipart(msg)

    def _forward_to_frontend_iopub(self, msg):
        print(f"F<P<K (IOPub) {msg}")
        self.iopub_stream.send_multipart(msg)

    def _forward_to_frontend_hb(self, msg):
        print(f"F<P<K (HB) {msg}")
        self.hb_stream.send_multipart(msg)

    def start(self):
        # Start the I/O loop
        loop = ioloop.IOLoop.current()
        while True:
            try:
                loop.start()
            except KeyboardInterrupt:
                print("Sending the interrupt signal to the kernel...")
                self.inner_kernel_process.send_signal(signal.SIGINT)


def find_free_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', 0))
        return s.getsockname()[1]

def read_connection_file(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

def write_connection_file(data, file_path):
    with open(file_path, 'w') as file:
        json.dump(data, file)

def launch_inner_kernel(new_connection_file):
    return subprocess.Popen(["python", "-m", "ipykernel_launcher", "-f", new_connection_file], stdout=sys.stdout, stderr=sys.stderr)

def main():
    parser = argparse.ArgumentParser(description="Jupyter Kernel Proxy Setup")
    parser.add_argument("-f", "--connection-file", required=True, help="Path to the Jupyter kernel connection file")
    args = parser.parse_args()

    original_connection_data = read_connection_file(args.connection_file)
    new_connection_data = original_connection_data.copy()

    # Generate new ports for the inner kernel
    for port_type in ['shell_port', 'iopub_port', 'stdin_port', 'control_port', 'hb_port']:
        new_connection_data[port_type] = find_free_port()

    ports = set()
    for port_type in ['shell_port', 'iopub_port', 'stdin_port', 'control_port', 'hb_port']:
        ports.add(new_connection_data[port_type])
        ports.add(original_connection_data[port_type])
    assert len(ports) == 10, "Ports are not unique"

    # Write the new connection file for the inner kernel
    new_connection_file = str(Path(args.connection_file).parent / "inner_kernel.json")
    write_connection_file(new_connection_data, new_connection_file)

    # Launch the inner kernel
    inner_kernel_process = launch_inner_kernel(new_connection_file)

    # Output frontend and kernel ports information
    frontend_ports = {k: original_connection_data[k] for k in new_connection_data if '_port' in k}
    kernel_ports = {k: new_connection_data[k] for k in new_connection_data if '_port' in k}
    print("Frontend Ports:", frontend_ports)
    print("Kernel Ports:", kernel_ports)

    ip = original_connection_data["ip"]

    proxy = JupyterKernelProxy(ip, frontend_ports, kernel_ports, inner_kernel_process)
    proxy.start()


if __name__ == "__main__":
    main()
