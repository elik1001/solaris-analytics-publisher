#!/usr/bin/env python


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

# Oracle Solaris RAD and Stats Store modules
import rad.auth as rada
import rad.client as radcli
import rad.connect as radcon
import rad.bindings.com.oracle.solaris.rad.sstore_1 as sstore

user = "root"
password = "password"

statsFields = [
  "date_time",
  "cpu.usage-sys",
  "cpu.usage-usr",
  "cpu.usage-total",
  "memory-used",
  "memory-total",
  "swap-used",
  "swap-total",
  "net.in-megabytes",
  "net.out-megabytes",
  "disk.read-megabytes-0B",
  "disk.write-megabytes-0B",
  "disk.read-ops-0B",
  "disk.write-ops-0B",
  "disk.read_wait-time-0B",
  "disk.write_wait-time-0B",
  "disk.read-megabytes-0C",
  "disk.write-megabytes-0C",
  "disk.read-ops-0C",
  "disk.write-ops-0C",
  "disk.read_wait-time-0C",
  "disk.write_wait-time-0C",
  "db1.ses-count",
  "db1.date_gen"
]


def get_value(val):
    if val.type == sstore.ValueType.NUMBER:
        return val.number
    elif val.type == sstore.ValueType.STRING:
        return val.string
    elif val.type == sstore.ValueType.STRING_ARRAY:
        return val.string_array
    elif val.type == sstore.ValueType.DICTIONARY:
        ret = {}
        for key in val.dictionary:
            ret[key] = get_value(val.dictionary[key])
  
        return ret
    else:
        return "Unsupported type"

def get_remote_data(link):

    o = urlparse(link)
    hostname = o.hostname.split('.')[0]

    data_ids = []
    for val in statsFields:
      data_ids.append("//:class.app/company/servers//:res.server/" + hostname + "//:stat." + val)
  
    reqs = {
        "data": sstore.BatchRequest(ssids=data_ids, range=None,
                                    req_type=sstore.RequestType.DATA_READ)
    }

    rc = radcon.connect_tls(hostname)
    auth = rada.RadAuth(rc)
    auth.pam_login(user, password)
    with radcon.connect_unix() as rc:

      while True:
        # Retrieve an instance of Info
        batch = rc.get_object(sstore.Batch())

        try:
          results = batch.read(requests=reqs, format=None)

          ssidStats = {}

          for tag in results:
            res = results[tag]

            if res.data is not None:
                for rec in res.data.records:
                    for pt in rec.points:
                        if pt.point_type == sstore.PointType.VALUE_POINT:
                            pt = pt.point_value
                            ts = pt.ts
                            ssidStats[rec.ssid ] = get_value(pt.value)

                # print all the warnings
                #if "warnings" in res.warnings:
                  #for warn in res.warnings:
                      #print("Failed to read info for {0}. Reason: {1}".format(
                          #warn.ssid, warn.reason))
            elif res.error is not None:
                print("Error: {0}. Reason: {1}".format(
                    res.error.action, res.error.reason))

          #print ssidStats
          updateSstore(ssidStats, hostname)

        except radcli.ObjectError as err:
          print("{0}. Reason: {1}".format(err.get_payload().action,
                                        err.get_payload().reason))
    rc.close()

def updateSstore(ssidStats, hostname):
   try:
       # ************** For DEBUG **************
       # The below can be used to pull from local then publish as "host" temp.
       # Will replace the ssid and re-write as host "temp".
       # Will replace the ssidStats and re-write as host "temp".

       ### Uncomment below for DEBUG only ###
       # Ssids  list
       #ssids = [
                #'//:class.app/company/servers//:res.server/' + "temp"
               #]
       ##print ssids

       #temp_ssidStats = {}
       #for key, val in ssidStats.iteritems() :
           #new_key = key.replace(hostname, "temp")
           #temp_ssidStats[new_key] = val
       #ssidStats = temp_ssidStats
       ### End of DEBUG ###

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

       time.sleep(2)

   except (KeyboardInterrupt, SystemExit):
       print "Caught KeyboardInterrupt, terminating workers"
       p.terminate()
       p.join()
       sys.exit(1)

def main():
    try:
      with open("/opt/sys_monitor/conf/s12-links.txt", "r") as f:
         links = f.read().splitlines()
      p = multiprocessing.Pool(processes=len(links))
      p.map(get_remote_data, (links))
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
