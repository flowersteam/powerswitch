#!/usr/bin/env python
# encoding: utf-8
"""
ePS4M.py

Created by Paul Fudal on 2014-01-30.
Copyright (c) 2014 INRIA. All rights reserved.
"""

import requests
import time
import subprocess
import threading
import pickle
import os
from threading import Thread
from netaddr import IPNetwork
import netifaces as ni

HIDDENPAGE_ = "/hidden.htm?"
GLOBALSTATUS = {'On': 0, 'Off' : 1, 'Restart' : 2, 'Rst' : 2}
DEFAULT_CONF_PATH = "~/.powerswitch/"
CONFIG_FILENAME = "config_"

def test_ip_mac_address(ip_address, mac_address):
    """Tests if real ips MAC address is equals to the given MAC address"""
    ret = subprocess.Popen(["sudo", "nmap", "-sP", "-n", ip_address],
                            stdout=subprocess.PIPE).stdout.read()
    ret_lines = ret.split('\n')[2:-2]
    mac = ret_lines[2].split(' ')[2].lower()
    return mac == mac_address

def get_mac_address(ip_address):
    """Get MAC address from ip"""
    ret = subprocess.Popen(["sudo", "nmap", "-sP", "-n", ip_address],
                            stdout=subprocess.PIPE).stdout.read()
    ret_lines = ret.split('\n')[2:-2]
    return ret_lines[2].split(' ')[2].lower()

def test_ip(ip_address):
    """Tests a http request at the specified ip on port 80"""
    try:
        rep = requests.get('http://' + ip_address + HIDDENPAGE_)
        return rep.status_code == 200
    except requests.ConnectionError:
        return False

def update_function(powerswitch):
    """Function called by the thread to update the power switch status"""
    while powerswitch.run_updater == True:
        powerswitch.update_status()
        time.sleep(0.5)

def search_on_network(mac_address):
    """Searches for the ip address on the given MAC address"""
    print "searching device {} on the network".format(mac_address)
    mac_dict = {}
    ifaces = ni.interfaces()
    for iface in ifaces:
        if not (iface.startswith('en') or iface.startswith('eth')):
            continue
        ifa = ni.ifaddresses(iface)
        try:
            ip_addr = ifa[2][0]['addr']
            mask = ifa[2][0]['netmask']
            prlen = IPNetwork(ip_addr + '/' + mask).prefixlen
            ret = subprocess.Popen(["sudo", "nmap", "-sP", "-n",
                                    str(ip_addr) + "/" + str(prlen)],
                                    stdout=subprocess.PIPE).stdout.read()
            ret_lines = ret.split('\n')[2:-4]
            count = 0
            while count < len(ret_lines):
                ip_s = ''
                mac = ''
                if ret_lines[count].startswith('Nmap'):
                    ip_s = ret_lines[count].split(' ')[4]
                    count = count + 1
                if ret_lines[count].startswith('Host'):
                    count = count + 1
                if ret_lines[count].startswith('MAC'):
                    mac = ret_lines[count].split(' ')[2].lower()
                    count = count + 1
                mac_dict[mac] = ip_s
        except KeyError:
            continue
    return mac_dict[mac_address]

class Eps4m(object):
    """Class defining a power switch"""
    def __init__(self, mac_address, load_config=False):
        if mac_address == None:
            raise ValueError("You must specify a MAC address for your device")
        self.status = {}
        self.lock = threading.Lock()
        self.addr = None
        self.mac_addr = None
        if load_config:
            self._load(mac_address)
            if mac_address != self.mac_addr:
                self.mac_addr = mac_address
                self.addr = search_on_network(mac_address)
            else:
                if not test_ip(self.addr):
                    self.addr = search_on_network(self.mac_addr)
            self._save()
        else:
            self.addr = search_on_network(mac_address)
            self.mac_addr = mac_address
        self.update_status()
        self.updater = Thread(target=update_function, args={self,})
        self.run_updater = True
        self.updater.daemon = True
        self.updater.start()

    def _save(self):
        """Saves the current configuration in the given file"""
        config_filepath = os.path.expanduser(DEFAULT_CONF_PATH
            + CONFIG_FILENAME + self.mac_addr.replace(":", "-"))
        if not os.path.exists(os.path.expanduser(DEFAULT_CONF_PATH)):
            os.makedirs(os.path.expanduser(DEFAULT_CONF_PATH))
        with open(config_filepath, 'w+') as filepath:
            config = {'ip' : self.addr, 'mac' : self.mac_addr}
            pickle.dump(config, filepath)

    def _load(self, mac_address):
        """Loads the configuration stired in the given file"""
        config_filepath = os.path.expanduser(DEFAULT_CONF_PATH
            + CONFIG_FILENAME + mac_address.replace(":", "-"))
        if os.path.isfile(config_filepath):
            with open(config_filepath, 'r') as filepath:
                config = pickle.load(filepath)
                self.addr = config['ip']
                self.mac_addr = config['mac']

    def update_status(self):
        """Updates the current status off the power switch"""
        self.lock.acquire()
        self._get_current_status()
        self.lock.release()

    def print_status(self):
        """Prints the current status of the power switch"""
        self.lock.acquire()
        print self.status
        self.lock.release()

    def set_on(self, port):
        """Puts the given port of the power switch on"""
        self._request(port, '=On')

    def is_on(self, port):
        """Returns true if given port is on"""
        self.update_status()
        return self.status[port] == 0

    def is_off(self, port):
        """Returns true if given port is off"""
        self.update_status()
        return self.status[port] == 1

    def is_restarting(self, port):
        """Returns true if given port is restarting"""
        self.update_status()
        return self.status[port] == 2

    def set_off(self, port):
        """Puts the given port of the power switch off"""
        self._request(port, '=Off')

    def restart(self, port):
        """Restarts the given port of the power switch"""
        self._request(port, '=Restart')

    def restart_in(self, port, time_s):
        """Restarts the given port of the power switch with a specified time"""
        assert time < 0
        self.set_off(port)
        time.sleep(time_s)
        self.set_on(port)

    def set_all_on(self):
        """Puts all ports of the power switch on"""
        for i in range(4):
            self.set_on(i)

    def set_all_off(self):
        """Puts allports of the power switch off"""
        for i in range(4):
            self.set_off(i)

    def all_restart(self):
        """Restarts all ports of the power switch"""
        for i in range(4):
            self.restart(i)

    def all_restart_in(self, time_s):
        """Restarts all ports of the power switch with the specified time"""
        for i in range(4):
            self.restart_in(i, time_s)

    def _get_current_status(self):
        """Retrieves the current status of the power switch"""
        rep = requests.get('http://' + self.addr + HIDDENPAGE_)
        rep.encoding = 'ISO-8859-1'
        status = str(rep.text).split('\n')[9:-3]
        for line in status:
            num_port = int(line[4:5])
            port_sta = line[6:-1]
            self.status[num_port - 1] = GLOBALSTATUS[port_sta]

    def _request(self, port, action):
        """Performs a request on the given port with the specified action"""
        assert 0 <= port < 4, \
            "port number are from 0 to 3; you asked for port {}".format(port)
        self.status[port] = GLOBALSTATUS[action[1:]]
        requests.get('http://' + self.addr + HIDDENPAGE_
                    + 'M0:O' + str(port+1) + action)
