#!/usr/bin/env python

import os
import sys
import time
import string
import sqlite3
import subprocess
from multiprocessing import Process
import psutil as ps

db1_host = "localhost"

db_files = {"monitor": { "db_filename": "/opt/sys_monitor/db/monitor.db", 
                         "schema_filename": "/opt/sys_monitor/db/sql_schema.sql"},
           "db1_qry":  { "db_filename": "/opt/sys_monitor/db/db1_qry-monitor.db",
                         "schema_filename": "/opt/sys_monitor/db/db1_qry-sql_schema.sql"}
           }

for x in db_files:
    db_file = db_files[x]["db_filename"]
    schema_file = db_files[x]["schema_filename"]

    db_is_new = not os.path.exists(db_file)

    with sqlite3.connect(db_file) as conn:
        if db_is_new:
            print 'Creating schema'
            with open(schema_file, 'rt') as f:
                schema = f.read()
            conn.executescript(schema)
            #conn.commit()
            #conn.close()
        else:
            print 'Database ', db_file, 'exists, assume schema ', schema_file, 'does, too.'
            #sys.exit(1)

# sleep at first to start stats
time.sleep(1)

def qryTime():
    start_time = int(time.time())
    subprocess.call(['/opt/sys_monitor/conf/test_db1_apps.sh', db1_host], stdout=subprocess.PIPE, shell=False, stderr=subprocess.PIPE)
    time.sleep(5)
    end_time = int(time.time())
    date_time = end_time
    db1_qry = end_time - start_time
    if db1_qry < 3:
       time.sleep(60)
    rowid = 1

    conn = sqlite3.connect('/opt/sys_monitor/db/db1_qry-monitor.db')
    cursor = conn.cursor()

    t =  [rowid, date_time, db1_qry ]
    conn.execute('INSERT OR REPLACE INTO db1Qry values (?,?,?)', t)
    #print t

    conn.commit()

def statTime():

    disks1 = ps.disk_io_counters(perdisk=True)
    dsk1_0b = disks1["sd1"]
    dsk1_0c = disks1["sd2"]
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
    dsk2_0c = disks2["sd2"]

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

    net2_all = net2["net1"]
    net_smb = (net2_all[0] - net1_all[0]) / 1024 / 1024 / 2
    net_rmb = (net2_all[1] - net1_all[1]) / 1024 / 1024 / 2

    ses_c = subprocess.Popen(['/opt/sys_monitor/conf/chk_db1_apps-ses.sh', db1_host], stdout=subprocess.PIPE, shell=False, stderr=subprocess.PIPE)
    stdout = ses_c.communicate()[0]
    db1_ses = filter(type(stdout).isdigit, stdout)
    rowid = 1

    conn = sqlite3.connect('/opt/sys_monitor/db/monitor.db')
    cursor = conn.cursor()

    t =  [rowid, date_time, cpu_usr, cpu_sys, cpu_tot,
              mem_usd, mem_tot, swp_usd, swp_tot,
              dsk_0b_rop, dsk_0b_wop, dsk_0b_rmb, dsk_0b_wmb, dsk_0b_rtm, dsk_0b_wtm,
              dsk_0c_rop, dsk_0c_wop, dsk_0c_rmb, dsk_0c_wmb, dsk_0c_rtm, dsk_0c_wtm,
              net_smb, net_rmb, db1_ses
             ]

    conn.execute('INSERT OR REPLACE INTO monitor values (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)', t)
    #print t

    conn.commit()

def chkDb():
    while True:
        qryTime()

def chkStats():
    while True:
        statTime()

if __name__=='__main__':
     p1 = Process(target = chkDb)
     p1.start()
     p2 = Process(target = chkStats)
     p2.start()
