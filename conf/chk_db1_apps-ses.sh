#!/usr/bin/env bash
### Export environment variable settings
. /opt/sys_monitor/conf/set_env

mysql -u root -ppassword -t <<!END
show status where \`variable_name\` = 'Threads_connected'
!END
