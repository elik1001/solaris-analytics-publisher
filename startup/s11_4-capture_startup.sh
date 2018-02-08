#!/bin/bash

case $1 in

   start) cd /opt/sys_monitor/bin
          nohup ./capture_from_local-s11_4.py &
   ;;
   stop) kill -9 `ps -ef |grep capture_from_local-s11_4.py|grep -v grep|awk '{print $2}'`
         exit 0
   ;;
   *) echo "Usage: $0 [start|stop]"
   ;;
esac
