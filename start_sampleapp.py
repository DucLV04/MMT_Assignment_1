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
from urllib.parse import parse_qs, unquote_plus 

from daemon.weaprous import WeApRous

PORT = 8000  # Default port
SERVER_IP = None
SERVER_PORT = None
PEER_IP = None
PEER_PORT = None
CONNECT_IP = None
CONNECT_PORT = None

PEER_LIST = "db/peer_list.txt"
MSG_HIST = "db/msg_hist.txt"

app = WeApRous()
'''
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
'''
# Add routes
# ===== TASK 1A: LOGIN AUTHENTICATION =====
@app.route("/login", methods=["POST"])
def login(headers, body):
    print("[SampleApp] login. request headers: {}, request body: {}".format(headers, body))
    data = {}
    if body:
        try:
            data = {k: v[0] for k, v in parse_qs(body).items()}
        except Exception:
            data = {}
    username = data.get('username', '')
    password = data.get('password', '')
    if username == "admin" and password == "password":#hardcoded for task1
        return 200
    else:
        return 401

@app.route("/logout", methods=["POST"])
def logout(headers, body):
    print("[SampleApp] logout. request headers: {}, request body: {}".format(headers, body))
    return 200

@app.route("/chat.html", methods=["GET"])
def chatPage(headers, body):
    print("[SampleApp] chat page. request headers: {}, request body: {}".format(headers, body))
    if (CONNECT_IP is None or CONNECT_PORT is None):
        return 404
    try:
        msg_list = []
        with open("www/chat_form.html", "r") as f:
            html = f.read()
        if (PEER_IP == CONNECT_IP and PEER_PORT == CONNECT_PORT):
            # If host peer, read direct from msg_hist.txt
            with open(MSG_HIST, "r") as f:
                msg_list = [line.strip() for line in f if line.strip()]
        else:
            # If peer, request chat history from host peer
            request = (
                f"GET /getChatHist HTTP/1.1\r\n"
            )
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((CONNECT_IP, CONNECT_PORT))
            s.sendall(request.encode())
            response = s.recv(4096).decode("utf-8")
            s.close()
            if response == "Disconnected":
                html = html.replace("{{addr}}", "Host has disconnected")
                html = html.replace("{{msgs}}", "")
                with open("www/chat.html", "w") as f:
                    f.write(html)
                return
            msg_list = [line.strip() for line in response.split('\n') if line.strip()]
        
        html = html.replace("{{addr}}", f"Chatroom: {CONNECT_IP}:{CONNECT_PORT}")
        msgs = ""
        for msg in msg_list:
            sender, content = msg.split(" - ")
            ip, port = sender.split(":")
            port = int(port)
            if (ip == CONNECT_IP and port == CONNECT_PORT):
                msgs += "<div class=\"message-wrapper host\">"
                msgs += f"<div class=\"name\">{sender}</div>"
                msgs += f"<div class=\"message host\">{content}</div>"
                msgs += "</div>"
            else:
                msgs += "<div class=\"message-wrapper user\">"
                msgs += f"<div class=\"name\">{sender}</div>"
                msgs += f"<div class=\"message user\">{content}</div>"
                msgs += "</div>"           
        html = html.replace("{{msgs}}", msgs)
        with open("www/chat.html", "w") as f:
            f.write(html)
        return 200
    except FileNotFoundError:
        raise FileNotFoundError
    
@app.route("/getChatHist", methods=["GET"])
def get_chat_hist(headers, body):
    print("[SampleApp] get chat hist for peer. request headers: {}, request body: {}".format(headers, body))
    return 200

# Peer-to-peer paradigm
@app.route("/connect", methods=["POST"])
def connect(headers, body):
    print("[SampleApp] connect to peer ip:port. request headers: {}, request body: {}".format(headers, body))
    global CONNECT_IP, CONNECT_PORT
    data = json.loads(body)
    addr = data.get("address")
    CONNECT_IP, CONNECT_PORT = addr.split(":")
    CONNECT_PORT = int(CONNECT_PORT)
    return 200

@app.route("/sendMsg", methods=["POST"])
def send_msg(headers, body):
    print("[SampleApp] send msg to {}:{}. request headers: {}, request body: {}".format(CONNECT_IP, CONNECT_PORT, headers, body))
    data = json.loads(body)
    msg = data.get("message")
    if (PEER_IP == CONNECT_IP and PEER_PORT == CONNECT_PORT):
        try:
            with open(MSG_HIST, "a") as f:
                f.write(PEER_IP + ":" + str(PEER_PORT) + " - " + msg + "\n")
        except FileNotFoundError:
            raise FileNotFoundError
    else:
        request = (
            f"POST /receiveMsg HTTP/1.1\r\n"
            f"\r\n"
            f"sender: {PEER_IP}:{PEER_PORT}\r\n"
            f"message: {msg}\r\n"
        )
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((CONNECT_IP, CONNECT_PORT))
        s.sendall(request.encode())
        s.close()
    return 200
    
@app.route("/receiveMsg", methods=["POST"])
def receive_msg(headers, body):
    print("[SampleApp] receive msg. request headers: {}, request body: {}".format(headers, body))
    lines = body.split('\r\n')
    data = {}
    for line in lines:
        if ': ' in line:
            key, val = line.split(': ', 1)
            data[key.lower()] = val
    sender = data.get("sender")
    msg = data.get("message")
    try:
        with open(MSG_HIST, "a") as f:
            f.write(sender + " - " + msg + "\n")
    except FileNotFoundError:
        raise FileNotFoundError
    return 200

# Client-server paradigm
@app.route("/submitInfo", methods=["POST"])
def submit_info(headers, body):
    # Peer function
    # Peer call this to forward its info to tracker and open a chatroom
    print("[SampleApp] This peer submit info to tracker. request headers: {}, request body: {}".format(headers, body))
    global CONNECT_IP, CONNECT_PORT
    CONNECT_IP = PEER_IP
    CONNECT_PORT = PEER_PORT
    try:
        open(MSG_HIST, "w").close()
    except FileNotFoundError:
        raise FileNotFoundError
    # Make socket connection and send request to tracker
    request = (
        f"POST /addInfo HTTP/1.1\r\n"
        f"\r\n"
        f"{PEER_IP}:{PEER_PORT}\r\n"
    )
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((SERVER_IP, SERVER_PORT))
    s.sendall(request.encode())
    s.close()
    return 200

@app.route("/addInfo", methods=["POST"])
def add_info(headers, body):
    # tracker function
    # tracker call this when receive peer request to add peer info to its list
    print("[SampleApp] tracker receive peer info and save to list. request headers: {}, request body: {}".format(headers, body))
    addr = body
    try:
        with open(PEER_LIST, "r") as f:
            saved_peer = [line.strip() for line in f if line.strip()]
        if addr not in saved_peer:
            with open(PEER_LIST, "a") as f:
                f.write(addr + "\n")
    except FileNotFoundError:
        raise FileNotFoundError
    return 200

@app.route("/getList", methods=["GET"])
def get_list(headers, body):
    # Peer function
    # Peer call this to forward its request to get peer_list from tracker
    print("[SampleApp] This peer request list of active peer. request headers: {}, request body: {}".format(headers, body))
    # Make socket connection and send request to tracker
    request = (
        f"GET /returnList HTTP/1.1\r\n"
    )
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((SERVER_IP, SERVER_PORT))
    s.sendall(request.encode())
    response = s.recv(4096)
    s.close()
    # Take response content (from /returnList of tracker) and write to this peer's index.html
    try:
        with open("www/index.html", "w") as f:
            f.write(response.decode("utf-8"))
    except FileNotFoundError:
        raise FileNotFoundError
    return 200

@app.route("/returnList", methods=["GET"])
def return_list(headers, body):
    # tracker function
    # tracker call this when receive peer request to get peer list
    try:
        with open(PEER_LIST, 'r') as f:
            pl = [line.strip() for line in f if line.strip()]
        with open("www/index_form.html", "r") as f:
            html = f.read()
        items = "".join(f"<option value=\"{p}\">{p}</option>" for p in pl)
        html = html.replace("{{ip_list}}", items)
        with open("www/index.html", "w") as f:
            f.write(html)
    except FileNotFoundError:
        raise FileNotFoundError
    return 200

@app.route("/disconnect", methods=["DELETE"])
def disconnect(headers, body):
    print("[SampleApp] disconnect. request headers: {}, request body: {}".format(headers, body))
    # If host peer, send request to delete itself from tracker peer list
    global CONNECT_IP, CONNECT_PORT
    if (PEER_IP == CONNECT_IP and PEER_PORT == CONNECT_PORT):
        request = (
            f"DELETE /deleteInfo HTTP/1.1\r\n"
            f"\r\n"
            f"{PEER_IP}:{PEER_PORT}\r\n"
        )
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((SERVER_IP, SERVER_PORT))
        s.sendall(request.encode())
        s.close()
    CONNECT_IP = None
    CONNECT_PORT = None
    try:
        with open(MSG_HIST, "w") as f:
            f.write("Disconnected")
    except FileNotFoundError:
        raise FileNotFoundError
    return 200
    

@app.route("/deleteInfo", methods=["DELETE"])
def delete_info(headers, body):
    # tracker function
    # tracker call this when receive peer request to add peer info to its list
    print("[SampleApp] tracker delete peer info from the list. request headers: {}, request body: {}".format(headers, body))
    deladdr = body.strip()
    try:
        with open(PEER_LIST, "r") as f:
            saved_peer = [line.strip() for line in f if line.strip()]
        with open(PEER_LIST, "w") as f:
            for addr in saved_peer:
                if addr != deladdr:
                    f.write(addr + "\n")      
    except FileNotFoundError:
        raise FileNotFoundError
    return 200

if __name__ == "__main__":
    # Parse command-line arguments to configure server IP and port
    parser = argparse.ArgumentParser(prog='Backend', description='', epilog='Beckend daemon')
    parser.add_argument('--server-ip', default='0.0.0.0')
    parser.add_argument('--server-port', type=int, default=PORT)
 
    args = parser.parse_args()
    SERVER_IP = args.server_ip
    SERVER_PORT = args.server_port

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('8.8.8.8',1))
        ip = s.getsockname()[0]
    except Exception:
        ip = '127.0.0.1'
    finally:
        PEER_IP = ip
        PEER_PORT = 8000
        s.close()
    
    print("This peer address: {}:{}".format(PEER_IP, PEER_PORT))

    # Delete existing peer list file before start
    try:
        open(PEER_LIST, "w").close()
        with open(MSG_HIST, "w") as f:
            f.write("Disconnected")
    except FileNotFoundError:
        raise FileNotFoundError

    # Prepare and launch the RESTful application
    app.prepare_address(PEER_IP, PEER_PORT)
    app.run()