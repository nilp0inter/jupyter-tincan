import argparse
import json
import socket
import subprocess
import sys

from .proxy import JupiterTinCanProxy

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

