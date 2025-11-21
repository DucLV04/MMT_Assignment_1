#
# Copyright (C) 2025 pdnguyen of HCMC University of Technology VNU-HCM.
# All rights reserved.
# This file is part of the CO3093/CO3094 course.
#
# WeApRous release
#
# The authors hereby grant to Licensee personal permission to use
# and modify the Licensed Source Code for the sole purpose of studying
# while attending the course
#

"""
daemon.request
~~~~~~~~~~~~~~~~~

This module provides a Request object to manage and persist 
request settings (cookies, auth, proxies).
"""
from .dictionary import CaseInsensitiveDict

class Request():
    """The fully mutable "class" `Request <Request>` object,
    containing the exact bytes that will be sent to the server.

    Instances are generated from a "class" `Request <Request>` object, and
    should not be instantiated manually; doing so may produce undesirable
    effects.

    Usage::

      >>> import deamon.request
      >>> req = request.Request()
      ## Incoming message obtain aka. incoming_msg
      >>> r = req.prepare(incoming_msg)
      >>> r
      <Request>
    """
    __attrs__ = [
        "method",
        "url",
        "headers",
        "body",
        "reason",
        "cookies",
        "routes",
        "hook",
    ]

    def __init__(self):
        #: HTTP verb to send to the server.
        self.method = None
        #: HTTP URL to send the request to.
        self.url = None
        #: dictionary of HTTP headers.
        self.headers = None
        #: HTTP path
        self.path = None        
        # The cookies set used to create Cookie header
        self.cookies = None
        #: request body to send to the server.
        self.body = None
        #: Routes
        self.routes = {}
        #: Hook point for routed mapped-path
        self.hook = None

    def extract_request_line(self, request):
        try:
            lines = request.splitlines()
            first_line = lines[0]
            print("[Request] First line: {}".format(first_line))
            method, path, version = first_line.split()

            if path == '/':
                path = '/index.html'
            if path == '/login':
                path = '/login.html'
        except Exception:
            return None, None, None

        return method, path, version
             
    def prepare_headers(self, request):
        """Prepares the given HTTP headers."""
        lines = request.split('\r\n')
        headers = {}
        for line in lines[1:]:
            if ': ' in line:
                key, val = line.split(': ', 1)
                headers[key.lower()] = val
        return headers

    def prepare(self, request, routes=None):
        """Prepares the entire request with the given parameters."""

        # Prepare the request line from the request header
        self.method, self.path, self.version = self.extract_request_line(request)
        print("[Request] {} path {} version {}".format(self.method, self.path, self.version))

        #
        # @bksysnet Preapring the webapp hook with WeApRous instance
        # The default behaviour with HTTP server is empty routed
        #
        # TODO manage the webapp hook in this mounting point
        #
        
        if not routes == {}:
            self.routes = routes
            self.hook = routes.get((self.method, self.path))
            #
            # self.hook manipulation goes here
            # ...
            #
        self.auth=True
        # Xử lý headers
        self.headers = self.prepare_headers(request)
        # Gán URL từ Host và path
        host = self.headers.get('host', '')
        if host:
            self.url = f"http://{host}{self.path}"
        else:
            self.url = self.path
        # Xử lý body nếu có
        self.prepare_body(request, files=None, json=None)
        # Xử lý cookies nếu có
        self.prepare_cookies(self.headers.get('cookie', ''))
        return

    def prepare_body(self, request):
        self.prepare_content_length(self.body)
        #
        # TODO prepare the request authentication
        # self.auth = ...
        parts = data.split('\r\n\r\n', 1)
        if len(parts) > 1:
            self.body = parts[1]
        else:
            self.body = ''
        return


    def prepare_content_length(self, body):
        self.headers["Content-Length"] = "0"
        #
        # TODO prepare the request authentication
        #
	# self.auth = ...
        return


    def prepare_auth(self):
        #
        # TODO prepare the request authentication
        #
	    # self.auth = ...
        if (self.cookies.get("auth") == "true"):
            self.auth = True
        else:
            self.auth = False
        return

    def prepare_cookies(self, cookie_header):
        cookies = {}
        if cookie_header:
            for pair in cookie_header.split(';'):
                if '=' in pair:
                    k, v = pair.strip().split('=', 1)
                    cookies[k] = v
        self.cookies = cookies
