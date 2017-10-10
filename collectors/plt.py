#!/usr/bin/python3.5
import os
from os import path as p
import json
import pandas as pd
import logging
import numpy as np

def read_load_time(_file):
    with open(_file) as _f:
        _data = json.load(_f)
    return float(_data[0]['load'])

def read_ttfb_time(_file):
    with open(_file) as _f:
        _data = json.load(_f)
    return float(_data[1]['objs'][0][1]['responseReceivedTime'])


def read_dns(_file):
    with open(_file) as _f:
        _data = json.load(_f)
    print(_data[-1].keys())
    #return float(_data[-1]['dnsTime'])
    #return float(_data[-1]['sockets_bytes_in'])
    return float(_data[-1]['dnsTime'])


def main():
    logging.getLogger().setLevel(logging.INFO)
    _experiment_dir = '/home/jnejati/PLTSpeed/desktop_ustest1'
    #_experiment_dir = '/home/jnejati/PLTSpeed/desktop_zatest1'
    _sites = os.listdir(_experiment_dir)
    _sites.sort()
    out_f = open('/home/jnejati/PLTSpeed/collectors/stats_us.csv', 'w')
    #out_f = open('/home/jnejati/PLTSpeed/collectors/stats_za.csv', 'w')
    for _site_dir in _sites:
        _site_dir = os.path.join(_experiment_dir, _site_dir)
        _runs = [x for x in os.listdir(_site_dir) if x.startswith('run')]
        _runs.sort(key=lambda tup: int(tup.split('_')[1]))
        _site_name = _site_dir.split('/')[-1]
        _load_value = []
        for _run_no in _runs:
            _run_dir = os.path.join(_site_dir, _run_no)
            _analysis_dir = os.path.join(_run_dir, 'analysis')
            _afile = os.listdir(_analysis_dir)
            _afile.sort()
            _load_list = []
            if len(_afile) == 1:
                _analysis_file = os.path.join(_analysis_dir, _afile[0])
                _load = read_load_time(_analysis_file)
                _load_list.append(_load)
        if _load_list:
            _load = np.median(np.array(_load_list))
            out_f.write(_site_name + ',' + str(_load) + '\n')
    out_f.close()
if __name__ == "__main__":
    main()
