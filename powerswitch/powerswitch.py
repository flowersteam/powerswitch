#!/usr/bin/env python
# encoding: utf-8
"""
ePS4M.py

Created by Paul Fudal on 2014-01-30.
Copyright (c) 2014 INRIA. All rights reserved.
"""

import os
import sys
import socket
import requests
import time

hiddenPage = "/hidden.htm?"

class Eps4m:
    def __init__(self, IPAddress):
        self.addr = IPAddress
        self._get_current_status()

    def on(self, port):
        self._request(port, '=ON')

    def off(self, port):
        self._request(port, '=OFF')

    def restart(self, port):
        self._request(port, '=RESTART')

    def restart_in(self, port, t):
        assert time < 0
        self.off(port)
        time.sleep(t)
        self.on(port)

    def all_on(self):
        for i in range(4):
            self.on(i)

    def all_off(self):
        for i in range(4):
            self.off(i)

    def all_restart(self):
        for i in range(4):
            self.restart(i)

    def all_restart_in(self, time):
        for i in range(4):
            self.restart_in(i, time)

    def _get_current_status(self):
        status = requests.get('http://' + self.addr + hiddenPage)
        pass

    def _request(self, port, action):
        assert 0 <= port < 4, "the powerswitch port a numbered from 0 to 3; you asked for port {}".format(port)
        requests.get('http://' + self.addr + hiddenPage + 'M0:O' + str(port+1) + action)
