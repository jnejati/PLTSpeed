#!/usr/bin/env python3.5
__author__ = 'jnejati'

#import experiments
import json
import webDnsSetup
import network_emulator
import os
from urllib.parse import urlparse
import time
import urllib.request
import urllib.response
import io
import gzip
import subprocess
import logging
import timeit

def _change_resolv_conf():
    RESOLV_CONF = '/etc/resolv.conf'
    with open (RESOLV_CONF, 'w') as _f:
        _f.write('nameserver         127.0.0.1\n')


def main():
    input_file = 'africa.txt'
    #_change_resolv_conf()
    _path =  '/home/jnejati/PLTSpeed/domains_list'
    webDnsSetup.clear_folder(_path)
    with open('/home/jnejati/PLTSpeed/res/' + input_file) as _sites:
        for _site in _sites:
            _site = _site.strip()
            logging.info('Navigating to: ' + _site)
            s1 = urlparse(_site)
            dnsHandler = webDnsSetup.setup_dns_recorder()
            time.sleep(5)
            try:
                node = '/home/jnejati/.nvm/versions/node/v6.9.5/bin/node'
                _node_cmd = [node, 'chrome_launcher.js', _site,  '_trace_file', '_summary_file', '_screenshot_file']
                subprocess.call(_node_cmd, timeout = 110)
            except subprocess.TimeoutExpired:
                 print("Timeout:  ", _site, run_no)
            dnsHandler.kill()
            time.sleep(15)
            os.rename(os.path.join(_path, 'domains_list.txt'), os.path.join(_path, (s1.netloc + '.txt')))
            time.sleep(15)
if __name__ == '__main__':
    main()
