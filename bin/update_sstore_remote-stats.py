#!/usr/bin/env python

import os
import sys
import time
import json
import socket
import subprocess
import multiprocessing
from pprint import pprint
from libsstore import SStore
from urlparse import urlparse
from functools import partial
from urllib2 import Request, urlopen, URLError

def updateSstore(link):
   o = urlparse(link)
   hostname = o.hostname.split('.')[0]
   sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
   sock.connect((hostname, 19099))
   while True:
     try:
       sock.send("get_stat")
       data = json.loads(sock.recv(1024))

       # Ssids  list
       ssids = [
                '//:class.app/company/servers//:res.server/' + hostname
               ]
       #print ssids

       if data["db1"]["db1_ses"] == "":
          db1_ses = 0
       else:
          db1_ses = data["db1"]["db1_ses"]


       # Ssids and stat list
       ssidStats = {
              "//:class.app/company/servers//:res.server/" + hostname + "//:stat.date_time": data["date"]["date_time"],
              "//:class.app/company/servers//:res.server/" + hostname + "//:stat.cpu.usage-sys": data["cpu"]["cpu_sys"],
              "//:class.app/company/servers//:res.server/" + hostname + "//:stat.cpu.usage-usr": data["cpu"]["cpu_usr"],
              "//:class.app/company/servers//:res.server/" + hostname + "//:stat.cpu.usage-total": data["cpu"]["cpu_tot"],
              "//:class.app/company/servers//:res.server/" + hostname + "//:stat.memory-used": data["memory"]["mem_usd"],
              "//:class.app/company/servers//:res.server/" + hostname + "//:stat.memory-total": data["memory"]["mem_tot"],
              "//:class.app/company/servers//:res.server/" + hostname + "//:stat.swap-used": data["swap"]["swp_usd"],
              "//:class.app/company/servers//:res.server/" + hostname + "//:stat.swap-total": data["swap"]["swp_tot"],
              "//:class.app/company/servers//:res.server/" + hostname + "//:stat.net.in-megabytes": data["network"]["net_rmb"],
              "//:class.app/company/servers//:res.server/" + hostname + "//:stat.net.out-megabytes": data["network"]["net_smb"],
              "//:class.app/company/servers//:res.server/" + hostname + "//:stat.disk.read-megabytes-0B": data["disk"]["dsk_0b_rmb"],
              "//:class.app/company/servers//:res.server/" + hostname + "//:stat.disk.write-megabytes-0B": data["disk"]["dsk_0b_wmb"],
              "//:class.app/company/servers//:res.server/" + hostname + "//:stat.disk.read-ops-0B": data["disk"]["dsk_0b_rop"],
              "//:class.app/company/servers//:res.server/" + hostname + "//:stat.disk.write-ops-0B": data["disk"]["dsk_0b_wop"],
              "//:class.app/company/servers//:res.server/" + hostname + "//:stat.disk.read_wait-time-0B": data["disk"]["dsk_0b_rtm"],
              "//:class.app/company/servers//:res.server/" + hostname + "//:stat.disk.write_wait-time-0B": data["disk"]["dsk_0b_wtm"],
              "//:class.app/company/servers//:res.server/" + hostname + "//:stat.disk.read-megabytes-0C": data["disk"]["dsk_0c_rmb"],
              "//:class.app/company/servers//:res.server/" + hostname + "//:stat.disk.write-megabytes-0C": data["disk"]["dsk_0c_wmb"],
              "//:class.app/company/servers//:res.server/" + hostname + "//:stat.disk.read-ops-0C": data["disk"]["dsk_0c_rop"],
              "//:class.app/company/servers//:res.server/" + hostname + "//:stat.disk.write-ops-0C": data["disk"]["dsk_0c_wop"],
              "//:class.app/company/servers//:res.server/" + hostname + "//:stat.disk.read_wait-time-0C": data["disk"]["dsk_0c_rtm"],
              "//:class.app/company/servers//:res.server/" + hostname + "//:stat.disk.write_wait-time-0C": data["disk"]["dsk_0c_wtm"],
              "//:class.app/company/servers//:res.server/" + hostname + "//:stat.db1.qry-time": data["db1"]["db1_qry"],
              "//:class.app/company/servers//:res.server/" + hostname + "//:stat.db1.ses-count": db1_ses,
              "//:class.app/company/servers//:res.server/" + hostname + "//:stat.db1.date_gen": data["db1"]["lst_qry"]
             }
       #print ssidStats

       # Get an instance of SStore class
       ss = SStore()

       # Add resources
       ss.resource_add(ssids)

       # enable persistent recording of the collection
       ss.enabled = True

       try:
           #print ssids
           #print ssidStats
           ss.data_update(ssidStats)
       except:
          print("Failed to update stats because {0}".format(ss.err_description))
          exit(1)

       # Check for warnings
       for w in ss.warnings():
          print("Failed to update stat {0} because {1}".format(w.id, w.description))

       #print ssidStats, hostname
       time.sleep(2)

     except (socket.error, ValueError):
       print "Caught exception socket.error :"
       time.sleep(4)
       sock.close()
       try:
          sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
          sock.connect((hostname, 19099))
       except socket.error:
          print "Caught exception socket.error : Connection refused"
       except (KeyboardInterrupt, SystemExit):
          print "Caught KeyboardInterrupt, terminating"
          sys.exit(1)
     except (KeyboardInterrupt, SystemExit):
       print "Caught KeyboardInterrupt, terminating workers"
       p.terminate()
       p.join()
       sys.exit(1)

def main():
    try: 
      with open("/opt/sys_monitor/conf/links.txt", "r") as f:
         links = f.read().splitlines()
      p = multiprocessing.Pool(processes=len(links))
      p.map(updateSstore, (links))
      p.close()
      p.join()
    except KeyboardInterrupt:
         print 'parent received ctrl-c'
         p.terminate()
         p.join()
         sys.exit(1)

if __name__ == '__main__':
    try:
      main()
    except (KeyboardInterrupt, SystemExit):
      print "Caught KeyboardInterrupt, terminating workers"
      sys.exit(1)
