#!/usr/bin/env python
"""
Trigger garage door
"""
import socket
import select
from http.server import HTTPServer, BaseHTTPRequestHandler

class S(BaseHTTPRequestHandler):
    def do_POST(self):
        global Secret
        global GarageIP
        global GaragePort
        if self.path == "/garage/touch":
            x = self.headers.get("Authorization")
            if x == Secret:
                notifyGarage(GarageIP, GaragePort)
                self.send_response(204)
            else:
                self.send_response(401)
        else:
            self.send_response(404)
        self.end_headers()

def run(server_class=HTTPServer, handler_class=S, addr="0.0.0.0", port=8088):
    server_address = (addr, port)
    httpd = server_class(server_address, handler_class)
    httpd.serve_forever()

def notifyGarage(host="10.0.1.127", port=1011):
    target = (host, port)
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.sendto(b"4\n", (target))
    s.close()
    s = None

if __name__ == "__main__":
    with open('/config/secret.txt', 'r') as f:
        global Secret
        Secret = f.read().strip()
    with open('/config/host.txt', 'r') as f:
        a = f.read().strip().split(':')
        global GarageIP
        global GaragePort
        GarageIP = a[0]
        GaragePort = int(a[1])
    print(f"will talk to {GarageIP}:{GaragePort}")

    run()
