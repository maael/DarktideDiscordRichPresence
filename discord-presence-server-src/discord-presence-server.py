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

def log(msg):
    timestamp = time.strftime("[%Y-%m-%d %H:%M:%S]")
    print(f"{timestamp} {msg}")

# -------------------------------
# Config + Discord RPC
# -------------------------------
def load_config():
    fallback = {
        "port": 3923,
        "client_id": "1440090558763761860"
    }
    base_dir = get_base_dir()
    cfg_path = os.path.join(base_dir, "config.json")
    log(f"Loading config from: {cfg_path}")
    try:
        with open(cfg_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        log("Couldn't read config, using fallback")
        return fallback

POLL_INTERVAL = 5

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
    try:
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        result = subprocess.run(
            ["tasklist"],
            startupinfo=startupinfo,
            creationflags=subprocess.CREATE_NO_WINDOW,
            stdin=subprocess.DEVNULL,      # <<< IMPORTANT
            stdout=subprocess.PIPE,        # instead of capture_output=True
            stderr=subprocess.PIPE,
            text=True,
            check=False,   # don't raise on non-zero exit
        )
        if result.returncode != 0:
            log(f"tasklist failed with code {result.returncode}: {result.stderr!r}")
            return False

        found = name.lower() in result.stdout.lower()
        log(f"is_process_running('{name}') -> {found}")
        return found

    except Exception as e:
        log(f"ERROR in is_process_running: {e!r}")
        log(traceback.format_exc())
        # Decide how you want to handle a failure; probably safest:
        return False

def watch_process():
    log("Process watcher started 2.")
    misses = 0
    while True:
        if not is_process_running(PROCESS_NAME):
            misses += 1
            log(f"Process '{PROCESS_NAME}' not found (miss {misses}).")
            if misses >= 3:   # e.g. 3 consecutive misses
                break
        else:
            misses = 0
        time.sleep(POLL_INTERVAL)

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
    httpd.timeout = POLL_INTERVAL
    log("HTTP server thread started.")
    while watcher.is_alive():
        httpd.handle_request()

    log(f"Watcher is alive?: {watcher.is_alive()}")

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
