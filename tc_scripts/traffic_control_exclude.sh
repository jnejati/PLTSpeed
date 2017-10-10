#!/bin/bash
tc qdisc del dev ifb0 root
tc qdisc del dev lo root
tc qdisc del dev lo ingress
modprobe ifb
ip link set dev ifb0 up
tc qdisc add dev lo ingress
tc qdisc add dev ifb0 handle 1: root htb default 11
tc class add dev ifb0 parent 1: classid 1:1 htb rate 20000Mbps
tc class add dev ifb0 parent 1:1 classid 1:11  htb rate 750Kbit
tc class add dev ifb0 parent 1:1 classid 1:12  htb rate 20000Mbit
tc qdisc add dev ifb0 parent 1:11 handle 10: netem delay 20ms
tc qdisc add dev ifb0 parent 1:12 handle 11: netem delay 0.5ms
tc qdisc add dev lo handle 1: root htb default 11
tc class add dev lo parent 1: classid 1:1 htb rate 20000Mbps
tc class add dev lo parent 1:1 classid 1:11 htb rate 1.5Mbit
tc qdisc add dev lo  parent 1:11 handle 10: netem delay 20ms
tc class add dev lo parent 1:1 classid 1:12 htb rate 20000Mbit
tc qdisc add dev lo  parent 1:12 handle 11: netem delay 0.5ms

#tc filter add dev lo  parent 1: protocol ip prio 1 u32 match ip dport 9222 0xffff match ip sport 9222 0xffff flowid 1:12
tc filter add dev lo  parent 1: protocol ip prio 1 u32 match ip dport 9222  0xffff flowid 1:12
tc filter add dev lo  parent 1: protocol ip prio 1 u32 match ip sport 9222  0xffff flowid 1:12
tc filter add dev lo parent ffff: protocol ip basic match "cmp(u16 at 0 layer transport lt 9221) and cmp(u16 at 0 layer transport gt 9223)" flowid 1:11 action mirred egress redirect dev ifb0
