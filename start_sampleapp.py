#
# Copyright (C) 2025 pdnguyen of HCMC University of Technology VNU-HCM.
# All rights reserved.
# This file is part of the CO3093/CO3094 course,
# and is released under the "MIT License Agreement". Please see the LICENSE
# file that should have been included as part of this package.
#
# WeApRous release
#
# The authors hereby grant to Licensee personal permission to use
# and modify the Licensed Source Code for the sole purpose of studying
# while attending the course
#


"""
start_sampleapp
~~~~~~~~~~~~~~~~~

This module provides a sample RESTful web application using the WeApRous framework.

It defines basic route handlers and launches a TCP-based backend server to serve
HTTP requests. The application includes a login endpoint and a greeting endpoint,
and can be configured via command-line arguments.
"""

import json
import socket
import argparse

from daemon.weaprous import WeApRous

PORT = 8000  # Default port
SERVER_IP = '192.168.31.244'
SERVER_PORT = 8000
PEER_IP = None
PEER_PORT = None

PEER_LIST = "db/peer_list.txt"

app = WeApRous()

@app.route('/login', methods=['POST'])
def login(headers="guest", body="anonymous"):
    """
    Handle user login via POST request.

    This route simulates a login process and prints the provided headers and body
    to the console.

    :param headers (str): The request headers or user identifier.
    :param body (str): The request body or login payload.
    """
    print("[SampleApp] Logging in {} to {}".format(headers, body))

@app.route('/hello', methods=['PUT'])
def hello(headers, body):
    """
    Handle greeting via PUT request.

    This route prints a greeting message to the console using the provided headers
    and body.

    :param headers (str): The request headers or user identifier.
    :param body (str): The request body or message payload.
    """
    print("[SampleApp] ['PUT'] Hello in {} to {}".format(headers, body))

# Add routes
@app.route("/", methods=["GET"])
def home(headers, body):
    print("[SampleApp] homepage. request headers: {}, request body: {}".format(headers, body))
    #return {"message": "Welcome to the RESTful TCP WebApp"}

@app.route("/submitInfo", methods=["POST"])
def submit_info(headers, body):
    # Peer call this to forward its info to central server
    print("[SampleApp] This peer submit info to central server. request headers: {}, request body: {}".format(headers, body))
    # Make socket connection and send request to central server
    request = (
        f"POST /addInfo HTTP/1.1\r\n"
        f"Host: {PEER_IP}:{PEER_PORT}\r\n"
    )
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((SERVER_IP, SERVER_PORT))
    s.sendall(request.encode())
    response = s.recv(4096).decode()
    print(response)
    s.close()

@app.route("/addInfo", methods=["POST"])
def add_info(headers, body):
    # Central server call this when receive peer request to add peer info to its list
    print("[SampleApp] Central server receive peer info and save to list. request headers: {}, request body: {}".format(headers, body))
    addr = headers.get("host")
    try:
        with open(PEER_LIST, "r") as f:
            saved_peer = set(line.strip() for line in f if line.strip())
    except FileNotFoundError:
        saved_peer = set()
    if addr not in saved_peer:
        with open(PEER_LIST, "a") as f:
            f.write(addr + "\n")
        print(f"[SampleApp] Saved new IP: {addr}")

@app.route("/getList", methods=["GET"])
def get_list(headers, body):
    # Peer call this to forward its request to get peer_list from central server
    print("[SampleApp] This peer request list of active peer. request headers: {}, request body: {}".format(headers, body))
    # Make socket connection and send request to central server
    request = (
        f"GET /returnList HTTP/1.1\r\n"
    )
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((SERVER_IP, SERVER_PORT))
    s.sendall(request.encode())
    response = s.recv(4096)
    s.close()
    # Take response content (from /returnList of central server) and write to this peer's index_havelist.html
    with open("www/index_havelist.html", "w") as f:
        f.write(response.decode("utf-8"))

@app.route("/returnList", methods=["GET"])
def return_list(headers, body):
    # Central server call this when receive peer request to get peer list
    with open(PEER_LIST, 'r') as f:
        pl = [line.strip() for line in f if line.strip()]
    with open("www/index.html", "r") as f:
        html = f.read()
    items = "".join(f"<li>{p}</li>" for p in pl)
    #Debug: print("[SampleApp] peer list items: {}".format(items))
    html = html.replace("{{ip_list}}", items)
    #Debug: print("[SampleApp] html: {}".format(html))
    with open("www/index_havelist.html", "w") as f:
        f.write(html)

if __name__ == "__main__":
    # Parse command-line arguments to configure server IP and port
    parser = argparse.ArgumentParser(prog='Backend', description='', epilog='Beckend daemon')
    parser.add_argument('--server-ip', default='0.0.0.0')
    parser.add_argument('--server-port', type=int, default=PORT)
 
    args = parser.parse_args()
    PEER_IP = args.server_ip
    PEER_PORT = args.server_port

    # Delete existing peer list file before start
    open(PEER_LIST, "w").close()

    # Prepare and launch the RESTful application
    app.prepare_address(PEER_IP, PEER_PORT)
    app.run()