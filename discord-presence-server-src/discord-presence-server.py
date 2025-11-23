import json
import os
import sys
import time
import traceback
from http.server import BaseHTTPRequestHandler, SimpleHTTPRequestHandler
import socketserver
from pypresence import Presence # pyright: ignore[reportMissingImports]
import threading
import subprocess

# -------------------------------
# Logging
# -------------------------------
def get_base_dir():
    if getattr(sys, 'frozen', False):
        return sys._MEIPASS
    return os.path.dirname(os.path.abspath(__file__))

def get_logs_dir():
    base = os.path.dirname(os.path.abspath(sys.argv[0]))
    logs = os.path.join(base, "logs")
    os.makedirs(logs, exist_ok=True)
    return logs

LOG_FILE = os.path.join(get_logs_dir(), "server.log")
open(LOG_FILE, "w").close()

def log(msg):
    timestamp = time.strftime("[%Y-%m-%d %H:%M:%S]")
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"{timestamp} {msg}\n")


# -------------------------------
# Config + Discord RPC
# -------------------------------
def load_config():
    base_dir = get_base_dir()
    cfg_path = os.path.join(base_dir, "config.json")
    log(f"Loading config from: {cfg_path}")
    with open(cfg_path, "r", encoding="utf-8") as f:
        return json.load(f)

config = load_config()

rpc = Presence(config["client_id"])
rpc.connect()
log("Discord RPC connected successfully.")

# -------------------------------
# HTTP Handler
# -------------------------------
class Handler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        # Override default stderr logging (invisible in --noconsole)
        log("HTTP: " + format % args)

    def _json(self, obj, code=200):
        try:
            data = json.dumps(obj).encode("utf-8")
            self.send_response(code)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)
            self.wfile.flush()   # <<< IMPORTANT FIX
        except Exception as e:
            log("ERROR sending JSON: " + str(e))
            log(traceback.format_exc())

    def do_GET(self):
        log(f"GET {self.path}")
        if self.path == "/health":
            self._json({"status": "ok"})
        else:
            self._json({"error": "not found"}, 404)

    def do_POST(self):
        log(f"POST {self.path}")
        try:
            length = int(self.headers.get("Content-Length", "0"))
            payload = json.loads(self.rfile.read(length).decode("utf-8")) if length else {}
        except:
            payload = {}
            log("Error parsing POST JSON")

        try:
            if self.path == "/presence/set":
                rpc.update(
                    state=payload.get("state", ""),
                    details=payload.get("details", ""),
                    large_image=payload.get("large_image"),
                    large_text=payload.get("large_text"),
                    small_image=payload.get("small_image"),
                    small_text=payload.get("small_text"),
                    start=time.time(),
                )
                log("Presence updated")
                self._json({"status": "presence set"})

            elif self.path == "/presence/clear":
                rpc.clear()
                log("Presence cleared")
                self._json({"status": "presence cleared"})

            else:
                self._json({"error": "not found"}, 404)

        except Exception as e:
            log("ERROR in POST: " + str(e))
            log(traceback.format_exc())
            self._json({"error": str(e)}, 500)

# # -------------------------------
# # Process watching
# # -------------------------------

PROCESS_NAME = "Darktide.exe"

def is_process_running(name: str) -> bool:
    startupinfo = subprocess.STARTUPINFO()
    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    result = subprocess.run(
        ["tasklist"],
        startupinfo=startupinfo,
        creationflags=subprocess.CREATE_NO_WINDOW,
        capture_output=True,
        text=True
    )
    return name.lower() in result.stdout.lower()

def watch_process():
    log("Process watcher started.")
    running = True
    while running:
        if not is_process_running(PROCESS_NAME):
            log(f"Process '{PROCESS_NAME}' not found.")
            running = False
        else:
            running = True
            time.sleep(5)

# -------------------------------
# Start server
# -------------------------------
def run():
    port = config.get("port", 3923)
    log(f"Starting threaded server on port {port}")

    # Start background watcher
    watcher = threading.Thread(target=watch_process, daemon=True)
    watcher.start()

    # Start server
    httpd = socketserver.TCPServer(("127.0.0.1", port), Handler)
    httpd.timeout = 5
    log("HTTP server thread started.")
    while watcher.is_alive():
        httpd.handle_request()

    log("Shutting down...")

    rpc.clear()
    rpc.close()

    log("Exited")

if __name__ == "__main__":
    try:
        run()
    except Exception as e:
        log("Fatal crash: " + str(e))
        log(traceback.format_exc())
