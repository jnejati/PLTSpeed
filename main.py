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
import csv 

def _change_resolv_conf():
    RESOLV_CONF = '/etc/resolv.conf'
    with open (RESOLV_CONF, 'w') as _f:
        _f.write('nameserver         127.0.0.1\n')


def main():
    default_net_profile =  {'download_rate':'5Mbit',
                  'download_delay':'150ms',
                  'download_loss':'0.0%',
                  'upload_rate':'5Mbit',
                  'upload_delay':'150ms',
                  'upload_loss':'0.0%'}
    start = timeit.default_timer()
    input_file = 'africa.txt'
    _domains_dir = '/home/jnejati/PLTSpeed/domains_list/'
    config_file = '/home/jnejati/PLTSpeed/confs/netProfiles.json'
    _change_resolv_conf()
    with open(config_file, 'r') as f:
        default_net_profile = json.load(f)[0]
        _path =  os.path.join('/home/jnejati/PLTSpeed', default_net_profile['device_type'] + '_' + default_net_profile['name'])
        webDnsSetup.clear_folder(_path)
    with open('/home/jnejati/PLTSpeed/res/' + input_file) as _sites:
        for _site in _sites:
            _site = _site.strip()
            logging.info('Navigating to: ' + _site)
            s1 = urlparse(_site)
            _site_data_folder = os.path.join(_path, s1.netloc)
            if not os.path.isdir(_site_data_folder):
                os.mkdir(_site_data_folder)
                os.mkdir(os.path.join(_site_data_folder, 'dns'))
            with open(os.path.join(_domains_dir, s1.netloc + '.txt'), newline='') as f:
                _domains = csv.reader(f, delimiter=',')
                _domains = [x for x in _domains][0]
            _domains = [x[:-1] for x in _domains[:-1]]       
            _domains.sort()
            ### ping Delays
            netp = webDnsSetup.ping_delays(_domains, default_net_profile)
            netns = network_emulator.NetworkEmulator('desktop', _domains, netp, default_net_profile)
            print('Setting up namespaces ...')
            netns.setup_namespace()
            print('Setting up link profiles ...')
            netns.set_profile()
            ### DNS delays
            time.sleep(5)
            dnsHandler = webDnsSetup.setup_dns(_domains)
            #webDnsSetup.setup_webserver(_domains, _site_recorded)
            webDnsSetup.setup_replay(_domains)
            time.sleep(60)
            for run_no in range(1):
                _run_data_folder = os.path.join(_site_data_folder, 'run_' + str(run_no))
                if not os.path.isdir(_run_data_folder):
                    os.mkdir(_run_data_folder)
                    _subfolders = ['trace', 'screenshot', 'analysis', 'summary']
                    for folder in _subfolders:
                        os.mkdir(os.path.join(_run_data_folder, folder))
                logging.info('Current profile: ' + default_net_profile['device_type'] + ' - ' + default_net_profile['name'] + ' run_no: ' + str(run_no) + ' site: ' + _site)
                os.system('pkill node')
                time.sleep(15)

                _trace_folder = os.path.join(_run_data_folder, 'trace')
                _screenshot_folder = os.path.join(_run_data_folder, 'screenshot')
                _summary_folder = os.path.join(_run_data_folder, 'summary')
                _trace_file = os.path.join(_trace_folder, str(run_no) + '_' + s1.netloc)
                _screenshot_file = os.path.join(_screenshot_folder, str(run_no) + '_' + s1.netloc)
                _summary_file = os.path.join(_summary_folder, str(run_no) + '_' + s1.netloc)
                logging.info(_trace_file, _screenshot_file, _summary_file)
                time.sleep(5)
                try:
                    node = '/home/jnejati/.nvm/versions/node/v6.9.5/bin/node'
                    _node_cmd = [node, 'chrome_launcher.js', _site,  _trace_file, _summary_file, _screenshot_file]
                    _cmd =  _node_cmd
                    subprocess.call(_cmd, timeout = 110)
                except subprocess.TimeoutExpired:
                    print("Timeout:  ", _site, run_no)
                    with open (os.path.join(_site_data_folder, 'log.txt'), 'w+') as _log:
                        _log.write("Timed out:  " +  _site + ' ' +  str(run_no) + '\n')
                time.sleep(1000)
            dnsHandler.kill()
            time.sleep(5)
    webDnsSetup.clear_ip_tables()
    stop = timeit.default_timer()
    logging.info(100*'-' + '\nTotal time: ' + str(stop -start)) 
if __name__ == '__main__':
    main()
