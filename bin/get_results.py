#!/usr/bin/env python

import os
import sys
import time
import json
import socket
import sqlite3
import threading
import psutil as ps

host = (socket.gethostname())
port = 19099
backlog = 10
size = 1024

def getDBData():

    #db_is_new = not os.path.exists(db_filename)

    rowid = 1

    db1qry_file = '/opt/sys_monitor/db/db1_qry-monitor.db'
    db = sqlite3.connect(db1qry_file)
    db.row_factory = sqlite3.Row
    conn = db.cursor()

    conn.execute('''SELECT * FROM db1Qry WHERE rowid=1''')
    for row in conn:
         db1_qry = row['db1_qry']
         lst_qry = row['date_time']


    mon_file = '/opt/sys_monitor/db/monitor.db'
    db = sqlite3.connect(mon_file)
    db.row_factory = sqlite3.Row
    conn = db.cursor()

    conn.execute('''SELECT * FROM monitor WHERE rowid=1''')
    for row in conn:
        data = { "date":     {"date_time": row['date_time']},
                 "cpu":      {"cpu_usr": row['cpu_usr'],
                              "cpu_sys": row['cpu_sys'],
                              "cpu_tot": row['cpu_tot']},
                 "memory":   {"mem_usd": row['mem_usd'],
                              "mem_tot": row['mem_tot']},
                 "swap":     {"swp_usd": row['swp_usd'],
                              "swp_tot": row['swp_tot']},
                 "disk":     {"dsk_0b_rop": row['dsk_0b_rop'],
                              "dsk_0b_wop": row['dsk_0b_wop'],
                              "dsk_0b_rmb": row['dsk_0b_rmb'],
                              "dsk_0b_wmb": row['dsk_0b_wmb'],
                              "dsk_0b_rtm": row['dsk_0b_rtm'],
                              "dsk_0b_wtm": row['dsk_0b_wtm'],
                              "dsk_0c_rop": row['dsk_0c_rop'],
                              "dsk_0c_wop": row['dsk_0c_wop'],
                              "dsk_0c_rmb": row['dsk_0c_rmb'],
                              "dsk_0c_wmb": row['dsk_0c_wmb'],
                              "dsk_0c_rtm": row['dsk_0c_rtm'],
                              "dsk_0c_wtm": row['dsk_0c_wtm']},
                 "network":  {"net_smb": row['net_smb'],
                              "net_rmb": row['net_rmb']},
                 "db1":      {"lst_qry": lst_qry,
                              "db1_qry": db1_qry,
                              "db1_ses": row['db1_ses']}
               }

    db.close()
    return json.dumps(data, indent=4, sort_keys=True)

class ThreadedServer(object):
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((self.host, self.port))

    def listen(self):
        self.sock.listen(backlog)
        while True:
            client, address = self.sock.accept()
            client.settimeout(15)
            threading.Thread(target = self.listenToClient,args = (client,address)).start()

    def listenToClient(self, client, address):
        while True:
             try:
              data = client.recv(1024)
              if data == "get_stat":
                new_data = getDBData()
                #print new_data
                client.send(new_data)
              else:
                new_data = getDBData()
                #print new_data
                client.send(new_data)
                client.close()
                return False
             except:
                client.close()
        client.close()

if __name__ == "__main__":
   ThreadedServer(host,port).listen()
