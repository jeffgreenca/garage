#!/usr/bin/env python
"""
Trigger garage door
"""
import requests
import socket
import json
from http.server import HTTPServer, BaseHTTPRequestHandler

class GarageLock:
    @staticmethod
    def Lock():
        GarageLock._set("locked")

    @staticmethod
    def Unlock():
        GarageLock._set("unlocked")

    @staticmethod
    def IsLocked():
        with open('garage.state', 'r') as f:
            state = f.read()
        if state == "unlocked":
            return False
        else:
            return True

    @staticmethod
    def _set(state):
        with open('garage.state', 'w') as f:
            f.write(state)
        print(f"set state to {state}", flush=True)
    

def notifyGarage():
    #host="10.0.1.127", port=1011
    global GarageIP
    global GaragePort
    target = (GarageIP, GaragePort)
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.sendto(b"4\n", (target))
    s.close()
    s = None

def notifyHuman(url="https://alert.vdc.sh/me", caller={}):
    info = ""
    if len(caller) > 0:
        info = f"\nclient {caller[0]}"

    try:
        requests.get(url, params={f"garage door{info}": ""}, timeout=2)
    except:
        print("could not notify human", flush=True)

class S(BaseHTTPRequestHandler):
    def _status(self, code, type='application/json'):
        self.send_response(code)
        # self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Content-type', type)
        self.end_headers()
    
    def _html(self, code, text):
        self._status(code, 'text/html')
        self.wfile.write(text.encode("utf-8"))

    def _json(self, code, data):
        self._status(code)
        self.wfile.write(json.dumps(data).encode("utf-8"))

    def do_POST(self):
        # authorization check
        x = self.headers.get("Authorization")
        if x != Secret:
            self._status(401)
            return

        # trigger garage
        if self.path == "/garage/touch":
            if GarageLock.IsLocked():
                self._json(400, {"error": "garage locked"})
                return

            notifyGarage()
            notifyHuman(caller=self.client_address)
            self.send_response(204)
            self.end_headers()
            return

        # manage lock state
        if self.path == "/garage/unlock":
            GarageLock.Unlock()
            self.send_response(204)
            self.end_headers()
            return

        if self.path == "/garage/lock":
            GarageLock.Lock()
            self.send_response(204)
            self.end_headers()
            return

        # default
        self._status(404)
    
    def do_GET(self):
        if self.path == "/":
            self._html(200, UI)
            return

        if self.path == "/garage/status":
            self._json(200, {"locked": GarageLock.IsLocked()})
            return

        # default
        self._status(404)

def run(server_class=HTTPServer, handler_class=S, addr="0.0.0.0", port=8088):
    server_address = (addr, port)
    httpd = server_class(server_address, handler_class)
    httpd.serve_forever()

if __name__ == "__main__":
    global Secret
    with open('/config/secret.txt', 'r') as f:
        Secret = f.readlines()[0].strip()

    global UI
    with open("/ui/ui.html", "r") as f:
        ui = f.read()
    UI = ui.replace("SECRET_TEMPLATE", Secret)

    global GarageIP
    global GaragePort
    with open('/config/host.txt', 'r') as f:
        a = f.read().strip().split(':')
        GarageIP = a[0]
        GaragePort = int(a[1])
    print(f"will talk to {GarageIP}:{GaragePort}", flush=True)

    GarageLock.Lock()

    run()
