from tempfile import NamedTemporaryFile
import argparse
import json
import socket
import subprocess
import sys
from pathlib import Path

from .proxy import JupiterTinCanProxy

def find_free_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', 0))
        return s.getsockname()[1]

def launch_inner_kernel(argv, new_connection_file):
    print(argv)
    argv[argv.index("{inner_kernel_connection_file}")] = new_connection_file
    return subprocess.Popen(argv, stdout=sys.stdout, stderr=sys.stderr)


def main():
    parser = argparse.ArgumentParser(description="Jupyter-TinCan Kernel Proxy")
    subparsers = parser.add_subparsers(dest='command', required=True)

    # Subcommand "create-kernel"
    create_kernel_parser = subparsers.add_parser('create-kernel', help='Create a new kernel configuration')
    create_kernel_parser.add_argument('config_folder', type=str, help='Path to the folder for the kernel configuration')

    # Subcommand "run"
    run_parser = subparsers.add_parser('run', help='Run the Jupyter-TinCan kernel proxy')
    run_parser.add_argument("-f", "--connection-file", required=True, help="Path to the Jupyter kernel connection file")
    run_parser.add_argument("--argv", type=json.loads, help="JSON-encoded array of strings for additional arguments")

    # Parse arguments
    args = parser.parse_args()

    if args.command == 'create-kernel':
        # Handle create-kernel command
        create_kernel(args.config_folder)
    elif args.command == 'run':
        # Handle run command
        run_kernel(args.connection_file, args.argv)

def create_kernel(config_folder):
    # Implement the logic for creating a new kernel configuration
    with open(str(Path(config_folder) / "kernel.json"), 'r') as file:
        kernel_config = json.load(file)
    new_kernel_config = kernel_config.copy()
    kernel_config["argv"][kernel_config["argv"].index("{connection_file}")] = "{inner_kernel_connection_file}"
    new_kernel_config["argv"] = ["python", "-m", "jupyter_tincan", "run", "-f", "{connection_file}", "--argv", json.dumps(kernel_config["argv"])]
    new_kernel_config["display_name"] = "🥫 " + kernel_config["display_name"]
    json.dump(new_kernel_config, sys.stdout, indent=2)


def run_kernel(connection_file, argv):
    # Implement the logic for running the kernel proxy

    with open(connection_file, 'r') as file:
        original_connection_data = json.load(file)
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
    with NamedTemporaryFile(mode='w', suffix=".json", prefix="jupyter_tincan_") as file:
        json.dump(new_connection_data, file)
        file.flush()

        # Launch the inner kernel
        inner_kernel_process = launch_inner_kernel(argv, file.name)

        # Output frontend and kernel ports information
        frontend_ports = {k: original_connection_data[k] for k in new_connection_data if '_port' in k}
        kernel_ports = {k: new_connection_data[k] for k in new_connection_data if '_port' in k}

        ip = original_connection_data["ip"]

        proxy = JupiterTinCanProxy(ip, frontend_ports, kernel_ports, inner_kernel_process)
        proxy.start()

