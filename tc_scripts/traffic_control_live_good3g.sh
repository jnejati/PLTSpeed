#!/bin/bash
tc qdisc del dev ifb0 root
tc qdisc del dev enp1s0f0 root
tc qdisc del dev lo root
tc qdisc del dev enp1s0f0 ingress
modprobe ifb
ip link set dev ifb0 up
tc qdisc add dev enp1s0f0 ingress

tc qdisc add dev enp1s0f0 handle 1: root htb default 11
tc class add dev enp1s0f0 parent 1: classid 1:1 htb rate 20000Mbps
tc class add dev enp1s0f0 parent 1:1 classid 1:11 htb rate 750Kbit
tc qdisc add dev enp1s0f0  parent 1:11 handle 10: netem delay 20ms
tc class add dev enp1s0f0 parent 1:1 classid 1:12 htb rate 20000Mbit
tc qdisc add dev enp1s0f0  parent 1:12 handle 11: netem delay 0.5ms
#tc filter add dev enp1s0f0 parent ffff: protocol ip basic match "cmp(u16 at 0 layer transport lt 21) and cmp(u16 at 0 layer transport gt 23)" flowid 1:11 action mirred egress redirect dev ifb0

tc filter add  dev enp1s0f0 parent ffff: protocol ip u32 match u32 0 0 flowid 1:11 action mirred egress redirect dev ifb0
#tc qdisc add dev ifb0 root netem delay 20ms 

tc qdisc add dev ifb0 handle 1: root htb default 11
tc class add dev ifb0 parent 1: classid 1:1 htb rate 20000Mbps
tc class add dev ifb0 parent 1:1 classid 1:11  htb rate 1.5Mbit
tc qdisc add dev ifb0 parent 1:11 handle 10: netem delay 20ms
tc class add dev ifb0 parent 1:1 classid 1:12  htb rate 20000Mbit
tc qdisc add dev ifb0 parent 1:12 handle 11: netem delay 0.5ms


tc qdisc add dev lo handle 2: root htb default 21
tc class add dev lo parent 2: classid 2:1 htb rate 20000Mbps
tc class add dev lo parent 2:1 classid 2:13 htb rate 20000Mbit

tc filter add dev enp1s0f0  parent 1: protocol ip prio 1 u32 match ip dport 22  0xffff flowid 1:12
tc filter add dev enp1s0f0  parent 1: protocol ip prio 1 u32 match ip sport 22  0xffff flowid 1:12

