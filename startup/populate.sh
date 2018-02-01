#!/usr/bin/env bash
set -x

nohup /opt/sys_monitor/bin/update_sstore_remote-stats.py &
exit 0
