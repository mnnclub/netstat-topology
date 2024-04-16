#!/bin/bash
# Tested with Amazon Linux 2

# $) netstat | head -n $Number_Of_HighLine
# The larger the number, then the higher the complexity with many of arrows
Number_Of_HighLine=3

IP=`/usr/sbin/route -n|grep ^0.0.0.0|awk '{print $8}'|xargs /usr/sbin/ifconfig |grep 'inet ' |awk '{print $2}'`

echo;echo \#$HOSTNAME;

/usr/bin/netstat -anpo |egrep -v LISTEN |egrep ^tcp|egrep "goodfys|java|beam|mongo|pips|redis|https\
|:(80|443|3010|3011|3020|3101|3306|5001|5002|5044|5672|6379|7888|8888|9600|9890|9888|15050|23001|23010|23011|61613|61616) " \
| awk '{print $5}' | sort -n|uniq -c |sort --key=1 -nr |head -${Number_Of_HighLine} |awk '{print $2,$1}' |sed "s/^/$IP /g"