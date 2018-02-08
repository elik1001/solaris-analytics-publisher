#!/usr/bin/python

import os
import sys
import time
import json
import string
import socket
import subprocess
import multiprocessing
from multiprocessing import Process
import psutil as ps
from pprint import pprint
from libsstore import SStore
from urlparse import urlparse
from functools import partial
from urllib2 import Request, urlopen, URLError

hostname = socket.gethostname()

def qryTime():
    start_time = int(time.time())
    subprocess.call(['/opt/sys_monitor/conf/test_db1_apps.sh', hostname], stdout=subprocess.PIPE, shell=False, stderr=subprocess.PIPE)
    time.sleep(5)
    end_time = int(time.time())
    date_time = end_time
    db1_qry = end_time - start_time
    if db1_qry < 3:
      time.sleep(60)

    statsData = {"db1.qry-time": db1_qry}

    #print statsData
    updateSstore(statsData)

def statTime():
    disks1 = ps.disk_io_counters(perdisk=True)
    dsk1_0b = disks1["sd1"]
    dsk1_0c = disks1["sd3"]
    net1 = ps.net_io_counters(pernic=True)
    net1_all = net1["net0"]

    time.sleep(2)

    date_time = int(time.time())
    cpu = ps.cpu_times_percent()
    mem = ps.virtual_memory()
    swap = ps.swap_memory()
    disks2 = ps.disk_io_counters(perdisk=True)
    net2 = ps.net_io_counters(pernic=True)

    cpu_usr = int(round(cpu[0],3))
    cpu_sys = int(round(cpu[1],3))
    cpu_tot = int(round(cpu[0] + cpu[1],3))
   
    # Conversion below - (0, 'B'), (10, 'KB'),(20, 'MB'),(30, 'GB'),(40, 'TB'), (50, 'PB')
    mem_usd = int(round(mem[3] / 2 ** 20))
    mem_tot = int(round(mem[0] / 2 ** 20))

    swp_usd = int(round(swap[1] / 2 ** 20))
    swp_tot = int(round(swap[0] / 2 ** 20))

    dsk2_0b = disks2["sd1"]
    dsk2_0c = disks2["sd3"]

    dsk_0b_rop = (dsk2_0b[0] - dsk1_0b[0])
    dsk_0b_wop = (dsk2_0b[1] - dsk1_0b[1])
    dsk_0b_rmb = (dsk2_0b[2] - dsk1_0b[2]) / 1024 / 1024
    dsk_0b_wmb = (dsk2_0b[3] - dsk1_0b[3]) / 1024 / 1024
    dsk_0b_rtm = (dsk2_0b[4] - dsk1_0b[4])
    dsk_0b_wtm = (dsk2_0b[5] - dsk1_0b[5])

    dsk_0c_rop = (dsk2_0c[0] - dsk1_0c[0]) 
    dsk_0c_wop = (dsk2_0c[1] - dsk1_0c[1])
    dsk_0c_rmb = (dsk2_0c[2] - dsk1_0c[2]) / 1024 / 1024
    dsk_0c_wmb = (dsk2_0c[3] - dsk1_0c[3]) / 1024 / 1024
    dsk_0c_rtm = (dsk2_0c[4] - dsk1_0c[4]) 
    dsk_0c_wtm = (dsk2_0c[5] - dsk1_0c[5])

    net2_all = net2["localnet0"]
    net_smb = (net2_all[0] - net1_all[0]) / 1024 / 1024 / 2
    net_rmb = (net2_all[1] - net1_all[1]) / 1024 / 1024 / 2

    ses_c = subprocess.Popen(['/opt/sys_monitor/conf/chk_db1_apps-ses.sh', hostname], stdout=subprocess.PIPE, shell=False, stderr=subprocess.PIPE)
    stdout = ses_c.communicate()[0]
    db1_ses = filter(type(stdout).isdigit, stdout)

    statsData = {
      "date_time": date_time,
      "cpu.usage-sys": cpu_sys,
      "cpu.usage-usr": cpu_usr,
      "cpu.usage-total": cpu_tot,
      "memory-used": mem_usd,
      "memory-total": mem_tot,
      "swap-used": swp_usd,
      "swap-total": swp_tot,
      "net.in-megabytes": net_rmb,
      "net.out-megabytes": net_smb,
      "disk.read-megabytes-0B": dsk_0b_rmb,
      "disk.write-megabytes-0B": dsk_0b_wmb,
      "disk.read-ops-0B": dsk_0b_rop,
      "disk.write-ops-0B": dsk_0b_wop,
      "disk.read_wait-time-0B": dsk_0b_rtm,
      "disk.write_wait-time-0B": dsk_0b_wtm,
      "disk.read-megabytes-0C": dsk_0c_rmb,
      "disk.write-megabytes-0C": dsk_0c_wmb,
      "disk.read-ops-0C": dsk_0c_rop,
      "disk.write-ops-0C": dsk_0c_wop,
      "disk.read_wait-time-0C": dsk_0c_rtm,
      "disk.write_wait-time-0C": dsk_0c_wtm,
      "db1.ses-count": int(db1_ses),
      "db1.date_gen": date_time
    }

    #print statsData
    updateSstore(statsData)

def createSstore():
   # Sleep at first to start stats
   time.sleep(1)

   try:
     # Ssids  list
     ssids = [
              '//:class.app/company/servers//:res.server/' + hostname
             ]
     #print ssids

     # Get an instance of SStore class
     ss = SStore()

     # Add resources
     ss.resource_add(ssids)

   except (KeyboardInterrupt, SystemExit):
     print "Caught KeyboardInterrupt, terminating workers"
     p.terminate()
     p.join()
     sys.exit(1)

def updateSstore(statsData):
   try:
     ssidStats = {}
     for key, val in statsData.iteritems() :
       ssidStats["//:class.app/company/servers//:res.server/" + hostname + "//:stat." + key] = val

     # Get an instance of SStore class
     ss = SStore()

     # enable persistent recording of the collection
     ss.enabled = True

     try:
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

   except (KeyboardInterrupt, SystemExit):
     print "Caught KeyboardInterrupt, terminating workers"
     p.terminate()
     p.join()
     sys.exit(1)

def chkDb():
    while True:
        qryTime()

def chkStats():
    while True:
        statTime()

if __name__=='__main__':
     createSstore()
     p1 = Process(target = chkStats)
     p1.start()
     p2 = Process(target = chkDb)
     p2.start()
