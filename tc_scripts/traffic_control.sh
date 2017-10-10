tc qdisc del dev ifb0 root
tc qdisc del dev lo root
tc qdisc del dev lo ingress
modprobe ifb
ip link set dev ifb0 up
tc qdisc add dev lo ingress
tc filter add dev lo parent ffff: protocol ip u32 match u32 0 0 flowid 1:1 action mirred egress redirect dev ifb0
tc qdisc add dev ifb0 handle 1: root htb default 11
tc class add dev ifb0 parent 1: classid 1:1 htb rate 1000Mbps
tc class add dev ifb0 parent 1:1 classid 1:11  htb rate 2Mbit 
tc qdisc add dev ifb0 parent 1:11 handle 10: netem delay 50ms 
tc qdisc add dev lo handle 1: root htb default 11
tc class add dev lo parent 1: classid 1:1 htb rate 1000Mbps
tc class add dev lo parent 1:1 classid 1:11 htb rate 2Mbit 
tc qdisc add dev lo  parent 1:11 handle 10: netem delay 50ms 

