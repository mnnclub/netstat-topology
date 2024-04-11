#!/bin/bash
# Tested with Amazon Linux 2

IP=`/usr/sbin/route -n|grep ^0.0.0.0|awk '{print $8}'|xargs /usr/sbin/ifconfig |grep 'inet ' |awk '{print $2}'`

echo;echo \#$HOSTNAME;

/usr/bin/netstat -anpo |egrep -v LISTEN |egrep ^tcp|egrep "goodfys|java|beam|mongo|pips|redis|https|:(80|443|3011|3306|23011) " \
| awk '{print $5}' | sort -n|uniq -c |sort --key=1 -nr |head -3|awk '{print $2,$1}' |sed "s/^/$IP /g"