#!/usr/bin/env python3.5
import base64
import json
import logging
import os
import signal
from datetime import datetime
from textwrap import wrap
from time import sleep

from dnslib import DNSLabel, QTYPE, RR, dns
from dnslib.proxy import ProxyResolver
from dnslib.server import DNSServer

import pickle
from ripe.atlas.sagan import PingResult
from ripe.atlas.sagan import DnsResult
from ripe.atlas.sagan.helpers import abuf
from ripe.atlas.cousteau import Measurement, Probe

SERIAL_NO = int((datetime.utcnow() - datetime(1970, 1, 1)).total_seconds())

handler = logging.StreamHandler()
handler.setLevel(logging.INFO)
handler.setFormatter(logging.Formatter('%(asctime)s: %(message)s', datefmt='%H:%M:%S'))

logger = logging.getLogger(__name__)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

TYPE_LOOKUP = {
    'A': (dns.A, QTYPE.A),
    'AAAA': (dns.AAAA, QTYPE.AAAA),
    'CAA': (dns.CAA, QTYPE.CAA),
    'CNAME': (dns.CNAME, QTYPE.CNAME),
    'DNSKEY': (dns.DNSKEY, QTYPE.DNSKEY),
    'MX': (dns.MX, QTYPE.MX),
    'NAPTR': (dns.NAPTR, QTYPE.NAPTR),
    'NS': (dns.NS, QTYPE.NS),
    'PTR': (dns.PTR, QTYPE.PTR),
    'RRSIG': (dns.RRSIG, QTYPE.RRSIG),
    'SOA': (dns.SOA, QTYPE.SOA),
    'SRV': (dns.SRV, QTYPE.SRV),
    'TXT': (dns.TXT, QTYPE.TXT),
    'SPF': (dns.TXT, QTYPE.TXT),
}


class Record:
    def __init__(self, rname, rtype, args):
        self._rname = DNSLabel(rname)

        rd_cls, self._rtype = TYPE_LOOKUP[rtype]
        if self._rtype == QTYPE.SOA and len(args) == 2:
            # add sensible times to SOA
            args += (SERIAL_NO, 3600, 3600 * 3, 3600 * 24, 3600),

        if self._rtype == QTYPE.TXT and len(args) == 1 and isinstance(args[0], str) and len(args[0]) > 255:
            # wrap long TXT records as per dnslib's docs.
            args = wrap(args[0], 255),

        if self._rtype in (QTYPE.NS, QTYPE.SOA):
            ttl = 3600 * 24
        else:
            ttl = 300

        if args.startswith('['):
            args = tuple(json.loads(args))
        else:
            args = (args,)

        self.rr = RR(
            rname=self._rname,
            rtype=self._rtype,
            rdata=rd_cls(*args),
            ttl=ttl,
        )

    def match(self, q):
        return q.qname == self._rname and (q.qtype == QTYPE.ANY or q.qtype == self._rtype)

    def sub_match(self, q):
        return self._rtype == QTYPE.SOA and q.qname.matchSuffix(self._rname)

    def __str__(self):
        return str(self.rr)


class Resolver(ProxyResolver):
    def __init__(self, upstream, records, delay_dict):
        super().__init__(upstream, 53, 5)
        self.records = records
        self.delay_dict = delay_dict

    def resolve(self, request, handler):
        type_name = QTYPE[request.q.qtype]
        reply = request.reply()
        for record in self.records:
            if record.match(request.q):
                reply.add_answer(record.rr)

        if reply.rr:
            print(float(self.delay_dict[str(request.q.qname)]) / 1000.0)
            if str(request.q.qname) in self.delay_dict:
                print('Zzz...!')
                sleep(self.delay_dict[str(request.q.qname)]/1000.0)
            logger.info('found zone for %s[%s], %d replies', request.q.qname, type_name, len(reply.rr))
            return reply

        # no direct zone so look for an SOA record for a higher level zone
        for record in self.records:
            if record.sub_match(request.q):
                reply.add_answer(record.rr)

        if reply.rr:
            if request.q.qname in self.delay_dict:
                print('Zzz')
                sleep(self.delay_dict[request.q.qname]/1000.0)
            logger.info('found higher level SOA resource for %s[%s]', request.q.qname, type_name)
            return reply

        logger.info('no local zone found, proxying %s[%s]', request.q.qname, type_name)
        return super().resolve(request, handler)


def handle_sig(signum, frame):
    logger.info('pid=%d, got signal: %s, stopping...', os.getpid(), signal.Signals(signum).name)
    exit(0)

def parse_ripe(_file="/home/jnejati/PLTSpeed/ripe/data/dns_data"):
    f  = open(_file, "rb")
    try:
        unpickler = pickle.Unpickler(f)
        dns_dict = unpickler.load()
    except EOFError:
        pass
    for i in range(len(dns_dict[''][''][20772]['responses'])):
        buf = str(dns_dict[''][''][20772]['responses'][1].abuf)
        print(type(buf), buf)
        raw_data = abuf.AbufParser.parse(base64.b64decode(buf))
        print(raw_data)
    exit()

if __name__ == '__main__':
    signal.signal(signal.SIGTERM, handle_sig)
    port = int(os.getenv('PORT', 53))
    address = '127.0.0.1'
    upstream = os.getenv('UPSTREAM', '8.8.8.8')
    zones = []
    record = Record('example.com', 'SOA', '["ns1.example.com", "dns.example.com"]')
    record = Record('www.example.com', 'A', '1.2.3.4')
    zones.append(record)
    record = Record('www.cnn.com', 'A', '2.2.2.2')
    zones.append(record)
    delay_dict = {'www.example.com.': 5000.0}
    resolver = Resolver(upstream, zones, delay_dict)
    udp_server = DNSServer(resolver, address=address, port=port)
    #tcp_server = DNSServer(resolver, port=port, tcp=True)

    logger.info('starting DNS server on port %d, upstream DNS server "%s"', port, upstream)
    #udp_server.start()
    udp_server.start_thread()
    #tcp_server.start_thread()
    #sleep(3)
    try:
        while udp_server.isAlive():
            sleep(1)
    except KeyboardInterrupt:
        pass
    #udp_server.stop()
