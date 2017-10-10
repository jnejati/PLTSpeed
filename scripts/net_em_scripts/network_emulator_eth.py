import subprocess
#import netifaces
import os

__author__ = 'jnejati'


class NetworkEmulator():

    def __init__(self, profile, domain_list):
        self.profile = profile
        self._netns = domain_list


    def set_profile(self, net_type):
        if self.profile['device_type'] == 'desktop':
            subprocess.call(['tc', 'qdisc', 'del', 'dev', 'eth0', 'root'])
            subprocess.call(['tc', 'qdisc', 'del', 'dev', 'lo', 'root'])
            subprocess.call(['tc', 'qdisc', 'del', 'dev', 'usb0', 'root'])
            print('Removing all current disciplines')
            for i in range(len(self._netns)):
                netns_a = 'netns-0'
                netns_b = 'netns-' + str(i + 1)
                veth_a = 'veth-' + str(i * 2)
                veth_b = 'veth-' + str((i * 2) + 1)
                subprocess.call(['ip', 'netns', 'exec', netns_a, 'tc', 'qdisc', 'del', 'dev', veth_a, 'root'])
                subprocess.call(['ip', 'netns', 'exec', netns_b, 'tc', 'qdisc', 'del', 'dev', veth_b, 'root'])
            print('Setting network condition')
            for i in range(len(self._netns)):
                netns_a = 'netns-0'
                netns_b = 'netns-' + str(i + 1)
                veth_a = 'veth-' + str(i * 2)
                veth_b = 'veth-' + str((i * 2) + 1)
                subprocess.call(['ip', 'netns', 'exec', netns_a, 'tc', 'qdisc', 'add', 'dev', veth_a, 'handle', '1:0', 'root', 'htb', 'default', '11'])
                subprocess.call(['ip', 'netns', 'exec', netns_a, 'tc', 'class', 'add', 'dev', veth_a, 'parent', '1:', 'classid', '1:1', 'htb', 'rate', '1000Mbps'])
                subprocess.call(['ip', 'netns', 'exec', netns_a, 'tc', 'class', 'add', 'dev', veth_a, 'parent', '1:1', 'classid', '1:11', 'htb', 'rate', self.profile['download_rate'], 'burst', '15K'])
                subprocess.call(['ip', 'netns', 'exec', netns_a, 'tc', 'qdisc', 'add', 'dev', veth_a, 'parent', '1:11', 'handle', '10', 'netem', 'delay', self.profile['download_delay'], 'loss', self.profile['download_loss']])

                subprocess.call(['ip', 'netns', 'exec', netns_b, 'tc', 'qdisc', 'add', 'dev', veth_b, 'handle', '1:', 'root', 'htb', 'default', '11'])
                subprocess.call(['ip', 'netns', 'exec', netns_b, 'tc', 'class', 'add', 'dev', veth_b, 'parent', '1:', 'classid', '1:1', 'htb', 'rate', '1000Mbps'])
                subprocess.call(['ip', 'netns', 'exec', netns_b, 'tc', 'class', 'add', 'dev', veth_b, 'parent', '1:1', 'classid', '1:11', 'htb', 'rate', self.profile['upload_rate'], 'burst', '15K'])
                subprocess.call(['ip', 'netns', 'exec', netns_b, 'tc', 'qdisc', 'add', 'dev', veth_b, 'parent', '1:11', 'handle', '10', 'netem', 'delay', self.profile['upload_delay'], 'loss', self.profile['upload_loss']])
                
                
        elif self.profile['device_type'] == 'mobile':
                commands = [
                'tc' + ' ' + 'qdisc' + ' ' + 'del' + ' ' + 'dev' + ' ' + 'veth0' + ' ' + 'root'
                , 'tc' + ' ' + 'qdisc' + ' ' + 'del' + ' ' + 'dev' + ' ' + 'usb0' + ' ' + 'root'
                , 'tc' + ' ' + 'qdisc' + ' ' + 'del' + ' ' + 'dev' + ' ' + 'ifb0' + ' ' + 'root'
                , 'tc' + ' ' + 'qdisc' + ' ' + 'del' + ' ' + 'dev' + ' ' + 'eth0' + ' ' + 'ingress'
                , 'modprobe' + ' ' + 'ifb'
                , 'ip' + ' ' + 'link' + ' ' + 'set' + ' ' + 'dev' + ' ' + 'ifb0' + ' ' + 'up'
                , 'tc' + ' ' + 'qdisc' + ' ' + 'add' + ' ' + 'dev' + ' ' + 'usb0' + ' ' + 'ingress'
                , 'tc' + ' ' + 'filter' + ' ' + 'add' + ' ' + 'dev' + ' ' + 'usb0' + ' ' + 'parent' + ' ' + 'ffff:' + ' ' + 'protocol' + ' ' + 'ip' + ' ' + 'u32' + ' ' + 'match' + ' ' + 'u32' + ' ' + '0' + ' ' + '0' + ' ' + 'flowid' + ' ' + '1:1' + ' ' + 'action' + ' ' + 'mirred' + ' ' + 'egress' + ' ' + 'redirect' + ' ' + 'dev' + ' ' + 'ifb0'


                , 'tc'+ ' ' + 'qdisc' + ' ' + 'add' + ' ' + 'dev' + ' ' + 'ifb0' + ' '  + 'handle' + ' ' + '1:' + ' ' + 'root' + ' ' + 'htb' + ' ' + 'default' + ' ' + '11'
                , 'tc' + ' ' + 'class' + ' ' + 'add' + ' ' + 'dev' + ' ' + 'ifb0' + ' ' + 'parent' + ' ' + '1:' + ' ' + 'classid' + ' ' + '1:1' + ' ' + 'htb' + ' ' + 'rate' + ' ' + '1000Mbps'
                , 'tc' + ' ' + 'class' + ' ' + 'add' + ' ' + 'dev' + ' ' + 'ifb0' + ' ' + 'parent' + ' ' + '1:1' + ' ' + 'classid' + ' ' + '1:11' + ' ' + 'htb' + ' ' + 'rate' + ' ' +  self.profile['download_rate']
                , 'tc' + ' ' + 'qdisc' + ' ' + 'add' + ' ' + 'dev' + ' ' + 'ifb0' + ' ' + 'parent' + ' ' + '1:11' + ' ' + 'handle' + ' ' + '10:' + ' ' + 'netem' + ' ' + 'delay' + ' ' + self.profile['download_delay'] + ' ' + 'loss' + ' ' + self.profile['download_loss']
                , 'tc' + ' ' + 'qdisc' + ' ' + 'add' + ' ' + 'dev' + ' ' + 'usb0' + ' ' + 'handle' + ' ' + '1:' + ' ' + 'root' + ' ' + 'htb' + ' ' + 'default' + ' ' + '11'
                , 'tc' + ' ' + 'class' + ' ' + 'add' + ' ' + 'dev' + ' ' + 'usb0' + ' ' + 'parent' + ' ' + '1:' + ' ' + 'classid' + ' ' + '1:1' + ' ' + 'htb' + ' ' + 'rate' +' ' +  '1000Mbps'
                , 'tc' + ' ' + 'class' + ' ' + 'add' + ' ' + 'dev' + ' ' + 'usb0' + ' ' + 'parent' + ' ' + '1:1' + ' ' + 'classid' + ' ' + '1:11' + ' ' + 'htb' + ' ' + 'rate' +' ' +  self.profile['upload_rate']
                , 'tc' + ' ' + 'qdisc' + ' ' + 'add' + ' ' + 'dev' + ' ' + 'usb0' + ' ' + 'parent' + ' ' + '1:11' + ' ' + 'handle' + ' ' + '10:' + ' ' + 'netem' + ' ' + 'delay' + ' ' + self.profile['upload_delay'] + ' ' + 'loss' + ' ' + self.profile['upload_loss']
]



def main():
    net_profile =  {'conn_type':'average_4g',
                  'device_type': 'desktop',
                  'page_type': 'inlined',
                  'cache': 'no_cache',
                  'download_rate':'10Mbit',
                  'download_delay':'50ms',
                  'download_loss':'0.0%',
                  'upload_rate':'10Mbit',
                  'upload_delay':'50ms',
                  'upload_loss':'0.0%'}
    path = '/var/www/original.testbed.localhost/www.alexa.com'
    dirs = os.listdir(path)
    print(dirs)
    my_ne = NetworkEmulator(net_profile, dirs)
    my_ne.set_profile('desktop')


if __name__ == '__main__':
    main()            
