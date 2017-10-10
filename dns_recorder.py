#!/usr/bin/env python3.5
import json
import logging
import os
import signal
import tldextract
from datetime import datetime
from pathlib import Path
from textwrap import wrap
from time import sleep

from dnslib import DNSLabel, QTYPE, RR, dns
from dnslib.proxy import ProxyResolver
from dnslib.server import DNSServer


SERIAL_NO = int((datetime.utcnow() - datetime(1970, 1, 1)).total_seconds())

handler = logging.StreamHandler()
handler.setLevel(logging.INFO)
handler.setFormatter(logging.Formatter('%(asctime)s: %(message)s', datefmt='%H:%M:%S'))

logger = logging.getLogger(__name__)
logger.addHandler(handler)
#logger.setLevel(logging.INFO)
logger.setLevel(logging.ERROR)

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
    def __init__(self, upstream):
        super().__init__(upstream, 53, 5)
        self._domains_list = set()
    
    def resolve(self, request, handler):
        type_name = QTYPE[request.q.qtype]
        reply = request.reply()
        if request.q.qname not in self._domains_list:
            self._domains_list.add(request.q.qname)
            self.dump_domains_list(request.q.qname)
        logger.info('no local zone found, proxying %s[%s]', request.q.qname, type_name)
        record = super().resolve(request, handler)
        return super().resolve(request, handler)
     
    def dump_domains_list(self, _d):
        _path = '/home/jnejati/PLTSpeed/domains_list'
        with open(os.path.join(_path, 'domains_list.txt'), 'a') as dl:
            dl.write(str(_d) + ',')

def handle_sig(signum, frame):
    #resolver.dump_domains_list()
    logger.info('pid=%d, got signal: %s, stopping...', os.getpid(), signal.Signals(signum).name)
    exit(0)


if __name__ == '__main__':
    signal.signal(signal.SIGTERM, handle_sig)
    port = int(os.getenv('PORT', 53))
    address = '127.0.0.1'
    upstream = os.getenv('UPSTREAM', '8.8.8.8')
    resolver = Resolver(upstream)
    udp_server = DNSServer(resolver, address=address,  port=port)
    #tcp_server = DNSServer(resolver, port=port, tcp=True)

    logger.info('starting DNS server on port %d, upstream DNS server "%s"', port, upstream)
    udp_server.start_thread()
    #tcp_server.start_thread()

    try:
        while udp_server.isAlive():
            sleep(1)
    except KeyboardInterrupt:
        #resolver.dump_domains_list()
        pass
