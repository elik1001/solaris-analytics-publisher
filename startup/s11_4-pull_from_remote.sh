#!/bin/bash
#set -x

case $1 in

   start) cd /opt/sys_monitor/bin
          nohup ./pull_from_remote-s11_4.py &
   ;;
   stop) kill -9 `ps -ef |grep pull_from_remote-s11_4.py|grep -v grep|awk '{print $2}'`
         exit 0
   ;;
   *) echo "Usage: $0 [start|stop]"
   ;;
esac
