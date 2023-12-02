import importlib.resources
import json
import subprocess


TEXT2SVG_JS_PATH = importlib.resources.files("jupyter_tincan") / "text2svg.js"


def node_text2svg():
    """
    Run the text2svg node worker.
    This is a generator you can send text to and it will return SVG.

    Example:
        worker = text2svg()
        next(worker)
        svg = worker.send("Hello World")
    """
    worker = subprocess.Popen(["node", str(TEXT2SVG_JS_PATH)], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    text = yield
    while True:
        worker.stdin.write(text.encode("utf-8"))
        worker.stdin.write(b"\n")
        worker.stdin.flush()
        svg = worker.stdout.readline().decode("utf-8")
        text = yield svg


class Text2SVG:
    """
    A class that wraps the text2svg node worker.
    """

    def __init__(self):
        self.worker = node_text2svg()
        next(self.worker)

    def __call__(self, text, size=16, fill="black", stroke="black"):
        payload = json.dumps({"attributes": {"fill": fill, "stroke": stroke},
                              "options": {"x": 0, "y": 0, "fontSize": size, "anchor": "top"},
                              "text": text})
        return self.worker.send(payload)
