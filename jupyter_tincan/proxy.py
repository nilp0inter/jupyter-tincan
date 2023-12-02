import json
import signal

import zmq
from tornado import ioloop
from zmq.eventloop.zmqstream import ZMQStream

from .html import HTML2SVG

class JupiterTinCanProxy:
    def __init__(self, ip, frontend_ports, kernel_ports, inner_kernel_process):
        self.context = zmq.Context()
        self.ip = ip
        self.frontend_ports = frontend_ports
        self.kernel_ports = kernel_ports
        self.inner_kernel_process = inner_kernel_process
        self._setup_proxy_sockets()
        self._setup_proxy_streams()
        self.html2svg = HTML2SVG()

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
        print(f"F<P<K (IOPub-pre) {msg}")
        topic, delimiter, hmac_sig, header, parent, metadata, content = msg

        content = json.loads(content.decode("utf-8"))
        if content.get("data", {}).get("text/html", None):
            content["data"]["text/html"] = self.html2svg(content["data"]["text/html"])
        elif content.get("name", None) == "stdout":
            # Transform it to html
            header = json.loads(header.decode("utf-8"))

            topic = b'kernel.7bb092de-d50e-4272-ad08-bd952ad7b131.execute_result'
            header["msg_type"] = "execute_result"
            content = {"data": {"text/html": self.html2svg(content["text"]), "text/plain": "*stdout*"}, "metadata": {}, "execution_count": 1}

            header = json.dumps(header).encode("utf-8")
        content = json.dumps(content).encode("utf-8")

        msg = [topic, delimiter, hmac_sig, header, parent, metadata, content]
        print(f"F<P<K (IOPub-post) {msg}")

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
