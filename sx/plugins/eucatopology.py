#!/usr/bin/env python

# (c) Copyright 2016 Hewlett Packard Enterprise Development Company LP
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; version 3 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see http://www.gnu.org/licenses/.
"""
This plugin provides a top level view of the Eucalyptus cloud and can 
be used as a starting point for troubleshooting the cloud.
This plugin uses sysreport/sosreports.

The plugin can be placed in the directory: $HOME/.sx/sxplugins/
$ cp demo.py $HOME/.sx/sxplugins/

It will need to be enabled.

@version   :  1.0 
"""
import os
import re
import pdb
import pprint
import shutil
import logging
import urlparse
import subprocess

from operator import itemgetter

import sx
import sx.plugins
from sx.logwriter import LogWriter

class Service(object):
    def __init__(self):
        self.hostname = ""
        self.url = ""
        self.arn = ""
        self.stype = ""
        self.zone = ""
        self.state = ""

    def no_name(self):
        return "<td>%s</td><td>%s</td><td>%s</td><td>%s</td>" % (self.url,self.state, self.arn, self.stype)
	
    def __str__(self):
        return '<td>%s</td><td>%s</td><td style="white-space: nowrap">%s</td><td>%s</td><td>%s</td><td>%s</td>' % (self.hostname, self.state, self.url, self.arn, self.stype, self.zone)


class Eucatopology(sx.plugins.PluginBase):
    """
    Eucalyptus Cloud Topology
    """
    def __init__(self, pathToPluginReportDir=""):
        """
        @param pathToPluginReportDir: This is the root path to where
        the report files will be written.
        @type pathToPluginReportDir: String
        """
        sx.plugins.PluginBase.__init__(self, "EucaTopology",
                                       "This plugin provides a topology view of the Eucalyptus cloud.",
                                       ["Sosreport", "Sysreport"], False, True,
                                       {},
                                       pathToPluginReportDir)
        self.__services = []
        self.__host_to_ereport = {}
        self.__ip_to_hostname = {}
        self.__hostname_to_ip = {}
        self.__ip_to_types = {}

    def setup(self, reports):
        """
        This function will setup data structure to hold any data/path
        to files that are needed to use in this plugin.

        @param reports: This is the list of Report Objects.
        @type reports: Array
        """
        # Always print this message if you going to call this function
        # so that logging is notified that this function has been called.
        message = "Running setup for plugin: %s" %(self.getName())
        logging.getLogger(sx.MAIN_LOGGER_NAME).status(message)
        ipv4_re = re.compile(".*inet addr:([0-9]+\.[0-9]+\.[0-9]+\.[0-9]+)")

        for report in reports:
            if self.isValidReportType(report):
                self.__host_to_ereport[report.getHostname()] = (report.getDate(),report.getPathToExtractedReport())
                #
                # Process euca-describe-services-all, should only be on one host
                #
                host_info = report.getDataFromFile("etc/hosts")
                for i in host_info:
                    lsplit = i.split()
                    if report.getHostname() in lsplit:
                        self.__ip_to_hostname[lsplit[0]] = lsplit[1:]
                        self.__hostname_to_ip.setdefault(report.getHostname(), set()).add(lsplit[0])

                #
                # Gather ip addr info from ifconfig output also, because sometimes the hosts file
                # doesn't have the correct information.
                #
                ip_addr_info = report.getDataFromFile("ifconfig")
                if ip_addr_info is not None:
                    ip_addrs = [m.group(1) for m in [ipv4_re.match(i) for i in ip_addr_info] if m is not None]
		    ip_addrs = set(ip_addrs)
		    ip_addrs.remove("127.0.0.1")
                    self.__hostname_to_ip.setdefault(report.getHostname(), set()).update(ip_addrs)

                euca_services_output = report.getDataFromFile("sos_commands/eucafrontend/euca-describe-services-all")
               
                # None value means that the file doesn't exist
                if euca_services_output is None:
                    continue

                services_list = [i[:-1].split('\t') for i in euca_services_output]  # strip newline before splitting
                for i in services_list:
                    if i[0] == 'SERVICE':
                        try:
                            s = Service()
                            s.hostname = i[3].strip()
                            s.url = i[6].strip()
                            s.arn = i[7].strip()
                            s.stype = i[1].strip()
                            s.state = i[4].strip()
                            s.zone = i[2].strip()
                            self.__services.append(s)

                            url_p = urlparse.urlparse(s.url)
                            self.__ip_to_types.setdefault(url_p.hostname, set()).add(s.stype)

                        except IndexError:
                            logging.getLogger(sx.MAIN_LOGGER_NAME).status("Error on line: %s" % i)

    def execute(self):
        """
        This function should be overriden by the child if any
        intensive tasks needs be ran. This function should be used for
        writing to report files with write() functions or reporting
        any test results to console.
        """
        message = "Running execute for plugin: %s" % (self.getName())
        logging.getLogger(sx.MAIN_LOGGER_NAME).status(message)

    def report(self):
        """
        This function is where the reporting is done to console or to
        report files via the write() function.
        """
        message = "Generating report for plugin: %s" % (self.getName())
        logging.getLogger(sx.MAIN_LOGGER_NAME).status(message)

        # #######################################################################
        # Write information gathered to console
        # #######################################################################
        self.clean()
        #
        #
        #
        filename = "EucalyptusReportMapping.html"
        self.write(filename, "+++")
        self.write(filename, 'title="Report Mapping"')
	self.write(filename, 'menu="main"')
	self.write(filename, 'weight="-50"')
        self.write(filename, "+++")
        self.write(filename, "")
        self.write(filename, '<table class="pure-table pure-table-bordered" style="width=100%">') 
        self.write(filename, '<thead>')
	self.write(filename, '<th>Hostname</th>')
	self.write(filename, '<th>IP</th>')
	self.write(filename, '<th>Component</th>')
	self.write(filename, '<th>Date </th>')
	self.write(filename, '<th>Path</th>')
	self.write(filename, '</thead>')
 	self.write(filename, '<tbody>')	
        # We want to sort by component.
        sorted_by_component = []
        for host in self.__host_to_ereport:
            ips = list(self.__hostname_to_ip[host])

            for ip in ips:
                if ip in self.__ip_to_types:
                    components = list(self.__ip_to_types[ip])
                    break  # we found a match, no need to proceed with the loop
            else:
                components = ["Not found", ]

            components.sort()
            sorted_by_component.append((host, components))
        
        for count, i in enumerate(sorted(sorted_by_component, key=itemgetter(1))):
            i = i[0]
            rdate, rpath = self.__host_to_ereport[i]
            ips = list(self.__hostname_to_ip[i])
            for ip in ips:
                if ip in self.__ip_to_types:
                    service_types = self.__ip_to_types[ip]
                    break
            else:
                service_types = ["Not Found", ]

            ips.sort(key=lambda x: [int(j) for j in x.split('.')])
	    self.write(filename, '<tr class="%s">' % "pure-table-odd" if count % 2 != 0 else "<tr>")
            self.write(filename, '<td style="white-space: nowrap">%s</td><td>%s</td><td>%s</td><td style="white-space: nowrap">%s</td><td style="white-space: nowrap">%s</td>' % (i, ",".join(ips), ",&#8203;".join(sorted(service_types)),rdate,rpath))
            self.write(filename, '</tr>')
        self.write(filename, '</tbody>')
        self.write(filename, '</table>')

	
        # #######################################################################
        # Write information gathered to a report file.
        # #######################################################################
        # This is the filename where we will write all the report
        # files we want to generate.
        filename = "EucalyptusTopology.html"

        # Write a header
        self.write(filename, "+++")
        self.write(filename, 'title="Topology"')
        self.write(filename, 'menu="main"')
        self.write(filename, 'weight="-100"')
        self.write(filename, "+++")

        data = [i for i in self.__services if i.stype not in ["cluster","node","storage"]]
        self.write(filename, "<h2> Top Level Cloud Components: </h2>")
        self.write(filename, "")
	self.write(filename, '<table class="pure-table pure-table-bordered">')
	self.write(filename, '<thead>')
        self.write(filename, "<th>Item</th><th>Endpoint</th><th>State</th><th>ARN</th><th>Type</th>")
	self.write(filename, '</thead>')

	self.write(filename, '<tbody>')
        for j, i in enumerate(data):

            # Need to figure out highlighting of cells 
            if i.state != "ENABLED":
                i.state = "(red). %s" % i.state
	    self.write(filename, '<tr class="%s">' % "pure-table-odd" if j % 2 != 0 else "<tr>")
            self.write(filename,"<td>%d</td>%s" % (j+1, i.no_name()))
	    self.write(filename, '</tr>')
        self.write(filename, '</tbody>')
	self.write(filename, '</table>')
        self.write(filename, '')

        # Cluster
        data = [i for i in self.__services if i.stype == "cluster"]
        self.write(filename, "<h2> Cluster Controllers:</h2>")
        self.write(filename, "")
        self.write(filename, '<table class="pure-table pure-table-bordered">')
        self.write(filename, "<thead>")
        self.write(filename, "<th>Item</th><th>Name</th><th>State</th><th>Endpoint</th><th>ARN</th><th>Type</th><th>Zone</th>")
        self.write(filename, "</thead>")
	self.write(filename, "<tbody>")
        for j, i in enumerate(data):
            if i.state != "ENABLED":
                i.state = "(red). %s" % i.state
            self.write(filename, '<tr class="%s">' % "pure-table-odd" if j % 2 != 0 else "<tr>")
            self.write(filename, "<td>%d</td>%s" % (j+1, i))
            self.write(filename, '</tr>')
        self.write(filename, "</tbody>")
        self.write(filename, "</table>")
        self.write(filename, "")

        # Write out Storage Controllers
        data = [i for i in self.__services if i.stype == "storage"]
        self.write(filename, "<h2> Storage: </h2>")
        self.write(filename, "")
        self.write(filename, '<table class="pure-table pure-table-bordered">')
        self.write(filename, '<thead>')
        self.write(filename, '<th>Item</th><th>Name</th><th>State</th><th>Endpoint</th><th>ARN</th><th>Type</th><th>Zone</th>')
        self.write(filename, '</thead>')
        self.write(filename, '<tbody>')
        
        for j, i in enumerate(data):
            if i.state != "ENABLED":
                i.state = "(red). %s" % i.state
            self.write(filename, '<tr class="%s">' % "pure-table-odd" if j % 2 != 0 else "<tr>")
            self.write(filename, "<td>%d</td>%s" % (j+1, i))
            self.write(filename, '</tr>')
        self.write(filename, "")
        self.write(filename, '</tbody>')
        self.write(filename, '</table>')

        # Write out Nodes
        data = [i for i in self.__services if i.stype == "node"]
        self.write(filename, "<h2> Nodes:</h2>")
        self.write(filename, "")
        self.write(filename, '<table class="pure-table pure-table-bordered">')
        self.write(filename, '<thead>')
        self.write(filename, "<th>Item</th><th>Name</th><th>State</th><th>Endpoint</th><th>ARN</th><th>Type</th><th>Zone</th>")
        self.write(filename, '</thead>')
        for j,i in enumerate(data):
            if i.state != "ENABLED":
                i.state = "(red). %s" % i.state
            self.write(filename, '<tr class="%s">' % "pure-table-odd" if j % 2 != 0 else "<tr>")
            self.write(filename,"<td>%d</td>%s" % (j+1,i))
            self.write(filename, '</tr>')
        self.write(filename, '</tbody>')
        self.write(filename, '</table>')

        # By Availability Zones
        data = [i for i in self.__services if i.stype == "cluster"]
        zones = set([i.zone for i in data])
        
        for z in zones:
            datac = ["Cluster", [i for i in self.__services if i.stype == "cluster" if i.zone == z]]
            datas = ["Storage", [i for i in self.__services if i.stype == "storage" if i.zone == z]]
            datan = ["Node", [i for i in self.__services if i.stype == "node" if i.zone == z]]
            self.write(filename, "<h2>Availability Zone: %s </h2>" % z)
            self.write(filename, '<table class="pure-table pure-table-bordered">')
            self.write(filename, '<thead>')
            self.write(filename, "<th>Item</th><th>Name</th><th>State</th><th>Endpoint</th><th>ARN</th><th>Type</th><th>Zone</th>")
            self.write(filename, '</thead>')
            self.write(filename, '<tbody>')
            j = 0
            for d in [datac, datas, datan]:
                name, data = d
                for i in data:
                    self.write(filename, '<tr class="%s">' % "pure-table-odd" if j % 2 != 0 else "<tr>")
                    self.write(filename, "<td>%d</td>%s" % (j+1,i))
                    self.write(filename, '</tr>')
                    j+=1
            self.write(filename, '</tbody>')
            self.write(filename, '</table>')

    def action(self):
        """
        This function performs some external task such as opening web
        browser or file viewer to view a file.
        """
        # Always print this message if you going to call this function
        # so that logging is notified that this function has been called.
        message = "Performing action for plugin: %s" %(self.getName())
        logging.getLogger(sx.MAIN_LOGGER_NAME).status(message)
        old_dir = self.getPathToPluginReportDir()
        h, t = os.path.split(old_dir)
        # Make sure content directory exists
        content_dir = os.path.join(h,"content")
        if not os.path.exists(content_dir):
                os.mkdir(content_dir)
        new_dir = os.path.join(content_dir,t)
        message = "Moving directory from %s to %s" % (old_dir, new_dir)
        logging.getLogger(sx.MAIN_LOGGER_NAME).status(message)
        if os.path.exists(new_dir):
            shutil.rmtree(new_dir)
        os.rename(old_dir, new_dir)

