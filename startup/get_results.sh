#!/usr/bin/env bash

case $1 in

   start) cd /opt/sys_monitor/bin
          nohup ./get_results.py &
   ;;
   stop) kill -9 `ps -ef |grep get_results.py|grep -v grep|awk '{print $2}'`
         exit 0
   ;;
   *) echo "Usage: $0 [start|stop]"
   ;;
esac
