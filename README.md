# solaris-analytics-publisher
Solaris Analytics Capture And Publisher

This repository contains Solaris 11.4+(12) Analytics Capture and Publisher code.
The sample code will help you getting quickly up and running, and possibly adding your own statistics as well.

<h3>Getting Started</h3>

<h4>Installation</h4>
<h4>Dependencies / Prerequisites</h4>
<b>The following Python libraries are required:</b>
<pre>
os,
sys,
time,
socket,
string,
json,
sqlite3,
threading,
subprocess,
multiprocessing,
psutil as ps,
from functools import partial,
from libsstore import SStore,
from multiprocessing import Process,
from pprint import pprint,
from urllib2 import Request, urlopen, URLError,
from urlparse import urlparse,
</pre>
<i>Note: </i>You can install libraries by running <i>pip install [library]</i>

<h4>Application Layout Details</h4>
The directory layout are explained below.
<ol>
<li><b>/opt/sys_monitor/conf:</b> contains configuration scripts</li>
<li><b>/opt/sys_monitor/bin:</b> python code to capture and exposed stats</li>
<li><b>/opt/sys_monitor/db:</b> contains local sqlite db with latest stat record</li>
<li><b>/opt/sys_monitor/services:</b> contains Solaris xml  service files</li>
<li><b>/opt/sys_monitor/startup:</b> smf startup helper scripts</li>
<li><b>/opt/sys_monitor/modules:</b> psutil module (only needed for install)</li>
<li><b>/opt/sys_monitor/statsSrc:</b> contains custom stats Src Json files</b></li>
</ol>

<h4>Usage examples</h4>
To use Analytics sample application.

<ol>
<li>Clone the git project in to /opt/sys_monitor with git clone. for example, git clone https://github.com/elik1001/solaris-analytics-publisher</li>
<li>On the target host, modify <i>/opt/sys_monitor/capture.py</i>, replace <i>db1_host</i> if listening for remote traffic (default is localhost).</li>
<li>Modify <i>/opt/sys_monitor/capture.py</i>, replace <i>disks1/sd1 and disk2/sd4</i> with your sd device - you can find your device with iostat -xc (left col).</li>
<li>Modify <i>/opt/sys_monitor/capture.py</i>, replace <i>net1/interface1 and disk2/interface2</i> with your network device - you can find your device with ipadm.</li>
<li><i>Optional: </i>Modify <i>/opt/sys_monitor/get_results.py</i>, replace <i>host</i> with your hostname (or localhost)</li>
<li>Modiyf/add you host to /opt/sys_monitor/conf/links.txt, this file contains the list of hosts to fetch results which will then be published to  Analytics(Sstore).</li>
<li>Add/replace <i>/opt/sys_monitor/conf/chk_db1_apps-ses.sh and /opt/sys_monitor/conf/test_db1_apps.sh</i> with your MySQL DB password (or if you allow localhost, just remove it)</li>
<li><i>Optional: </i>Add any MySQL required variables to /opt/sys_monitor/conf/set_env</li>
</ol>

First Copy the Stats Store (sstore) custom json files to the stats directory.
<pre>
cp /opt/sys_monitor/statsSrc/*.json /usr/lib/sstore/metadata/json/site
</pre>
Now, restart the Stats Store service for the new stats to be available.
<pre>
svcadm restart svc:/system/sstore:default
</pre>

To use the application, you will need to import the SMF services, by running the below..
<ol>
<li>svccfg import /opt/sys_monitor/services/capture_service.xml</li>
<li>svccfg import /opt/sys_monitor/services/getresults_service.xml</li>
<li>svccfg import /opt/sys_monitor/services/populate_service.xml</li>
</ol>

Make sure the services are up and running, by running the below.
<pre>
svcs svc:/application/stats_capture:default svc:/application/stats_result:default svc:/application/monitor/update_stats:default
STATE          STIME    FMRI
online         12:58:35 svc:/application/stats_capture:default
online         12:58:35 svc:/application/stats_result:default
online         12:59:33 svc:/application/monitor/update_stats:default
</pre>

You are now ready to add stats to the Solaris GUI dashboard.
Login to https://localhost:6787/

<ul>
<li>In the Dashboard, click on the right side on Applications and select Solaris Analytics.</li>
<li>Click Add sheet, then give it a name</li>
<li>Click on Add a Visualization, then click on the left side gear and select add statistic</li>
<li>Now select, I want to enter a new statistic</li>
<li>Now you have plenty of options, but I will show one example below
<br>In <b>Class :</b> app/company/servers
<br>In <b>Resource:</b> server/your_server_name (or *)
<br>In <b>Statistic: </b> db1.ses-count
<br>In <b>Operation: (optional)</b> sum
</li>
</ul>

<p>A sample screen shut is below.
<br><img src="images/Solaris-analytics-3.png" alt="Solaris analytics" align="middle" height="50%"></p>

<h4>License</h4>
This project is licensed under the MIT License - see the LICENSE file for details.
