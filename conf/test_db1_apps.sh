#!/usr/bin/env bash 
#set -x
### Export environment variable settings
. /opt/sys_monitor/conf/set_env

mysql -u root -ppassword -t <<!END
use wordpress;
select count(*) from wp_posts;
!END

