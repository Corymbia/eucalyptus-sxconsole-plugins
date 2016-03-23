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
This plugin provides a top level view of the Eucalyptus cloud 
configuration, both via properties and /etc/eucalyptus/eucalyptus.conf 

The plugin can be placed in the directory: $HOME/.sx/sxplugins/
$ cp demo.py $HOME/.sx/sxplugins/

It will need to be enabled.

@version   :  1.0 
"""
import os
import pdb
import pprint
import shutil
import logging
import subprocess

import sx
import sx.plugins
from sx.logwriter import LogWriter


class Eucaconfig(sx.plugins.PluginBase):
    """
    Eucalyptus Configuration  
    """

    def __init__(self, pathToPluginReportDir=""):
        """
        @param pathToPluginReportDir: This is the root path to where
        the report files will be written.
        @type pathToPluginReportDir: String
        """
        sx.plugins.PluginBase.__init__(self, "EucaConfig",
                                       "This plugin provides a list of possible process issues.",
                                       ["Sosreport", "Sysreport"], False, True,
                                       {},
                                       pathToPluginReportDir)
        self.euca_properties = {}
        self.host_configs = {}
        # Add properties that you want highlighted here in the html report..
        self.highlight_properties = {"cloud.network.network_configuration": "json",
                                     }

        self.default_conf_values = {"EUCA_USER": '"eucalyptus"',
                                    "CLOUD_OPTS": '""',
                                    "CREATE_SC_LOOP_DEVICES": '256',
                                    "LOGLEVEL": '"INFO"',
                                    "DISABLE_REVERSE_LOOKUPS": '"Y"',
                                    "LOGROLLNUMBER": '"10"',
                                    "LOGMAXSIZE": '104857600',
                                    "NC_PORT": '"8775"',
                                    "CC_PORT": '"8774"',
                                    "SCHEDPOLICY": '"ROUNDROBIN"',
                                    "NODES": '""',
                                    "DISABLE_TUNNELING": '"Y"',
                                    "NC_SERVICE": '"axis2/services/EucalyptusNC"',
                                    "HYPERVISOR": '"kvm"',
                                    "USE_VIRTIO_ROOT": '"1"',
                                    "USE_VIRTIO_DISK": '"1"',
                                    "USE_VIRTIO_NET": '"1"',
                                    "MAX_CORES": '"8"',
                                    "NC_WORK_SIZE": '50000',
                                    "NC_CACHE_SIZE": '50000',
                                    "CONCURRENT_DISK_OPS": '4',
                                    "CREATE_NC_LOOP_DEVICES": '256',
                                    "INSTANCE_PATH": '"/var/lib/eucalyptus/instances"',
                                    "NC_BUNDLE_UPLOAD_PATH": '"/usr/bin/euca-bundle-upload"',
                                    "NC_CHECK_BUCKET_PATH": '"/usr/bin/euca-check-bucket"',
                                    "NC_DELETE_BUNDLE_PATH": '"/usr/bin/euca-delete-bundle"',
                                    "NC_MIGRATION_READY_THRESHOLD": '900',
                                    "WALRUS_DOWNLOAD_MAX_ATTEMPTS": '9',
                                    "CEPH_USER_NAME": '"nc_euca"',
                                    "CEPH_KEYRING_PATH": '"/etc/ceph/ceph.client.nc_euca.keyring"',
                                    "CEPH_CONFIG_PATH": '"/etc/ceph/ceph.conf"',
                                    "USE_CPU_PASSTHROUGH": '"0"',
                                    "VNET_MODE": '""',
                                    "VNET_PRIVINTERFACE": '"br0"',
                                    "VNET_PUBINTERFACE": '"br0"',
                                    "VNET_BRIDGE": '"br0"',
                                    "VNET_PUBLICIPS": '"your-free-public-ip-1 your-free-public-ip-2 ..."',
                                    "VNET_SUBNET": '"192.168.0.0"',
                                    "VNET_NETMASK": '"255.255.0.0"',
                                    "VNET_ADDRSPERNET": '"32"',
                                    "VNET_DNS": '"your-dns-server-ip"',
                                    "VNET_DOMAINNAME": '"eucalyptus.internal"',
                                    "VNET_LOCALIP": '"your-public-interface\'s-ip"',
                                    "VNET_DHCPDAEMON": '"/usr/sbin/dhcpd"',
                                    "VNET_DHCPUSER": '"dhcpd"',
                                    }
        self.default_property_values = {}

    def setup(self, reports):
        """
        This function will setup data structure to hold any data/path
        to files that are needed to use in this plugin.

        @param reports: This is the list of Report Objects.
        @type reports: Array
        """
        # Always print this message if you going to call this function
        # so that logging is notified that this function has been called.
        message = "Running setup for plugin: %s" % (self.getName())
        logging.getLogger(sx.MAIN_LOGGER_NAME).status(message)

        #
        # The geneneral method of getting configuration values will be as follows:
        # 1 - try to find the CLC properties (which are found via euca-describe-properties output)
        # 2 - try to locate /etc/eucalyptus/eucalyptus.conf
        #
        for report in reports:

            # It is possible that a property value spans multiple lines (like the network configuration). In this case we need
            # to read in the values carefully as apposed to just splitting the line.
            key = None
            rd = report.getDataFromFile("sos_commands/eucafrontend/euca-describe-properties")
            if rd is not None:
                for i in rd:
                    i = i[:-1]  # chop newline
                    if i.startswith("PROPERTY"):
                        data = i.split(None, 2)[1:]  # We don't care about the 'PROPERTY' field
                        key = data[0]
                        value = data[1]
                        self.euca_properties.setdefault(key, []).append(value)
                    else:
                        # append to last property until we reach a new state (read: PROPERTY)
                        if key is not None:
                            self.euca_properties[key].append(i)

            euca_conf_file = report.getDataFromFile("etc/eucalyptus/eucalyptus.conf")
            if euca_conf_file is not None:
                # need to strip the front of th estring possibly too...
                conf_data = [tuple(i[:-1].split('=', 1))
                             for i in euca_conf_file
                             if not i.startswith("#")
                             if len(i.strip()) > 0]
                self.host_configs[report.getHostname()] = conf_data

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
        # There should only be one
        #
        if len(self.euca_properties) > 0:
            filename = "EucalyptusConfig.html"
            self.write(filename, "+++")
            self.write(filename, 'title="Cloud Configuration"')
            self.write(filename, "weight=-1000")
            self.write(filename, "+++")
            self.write(filename, "")
            self.write(filename, "<h2> Properties </h2>")
            self.write(filename, "")
            self.write(filename, '<table class="pure-table pure-table-bordered">')
            self.write(filename, '<thead>')
            self.write(filename, "<th>Property</th><th>Value</th>")
            self.write(filename, '</thead>')
            self.write(filename, '<tbody>')
            for j, i in enumerate(sorted(self.euca_properties)):
                # Lets treat the network config as a code highlight
                value = "\n".join(self.euca_properties[i])
                if i in self.highlight_properties:
                    lang = self.highlight_properties[i]
                    value = "<pre>" + value + "</pre>"

                self.write(filename, '<tr class="%s">' % 'pure-table-odd' if j % 2 != 0 else '<tr>')
                self.write(filename, "<td>%s</td><td>%s</td>" % (i, value))
                self.write(filename, '</tr>')
            self.write(filename, '</tbody>')
            self.write(filename, '</table>')

        #
        # eucalyptus.conf files
        #
	td_class_color = ''
        for host in self.host_configs:
            filename = "%s.md" % host
            self.write(filename, '+++')
            self.write(filename, 'title="Config for host %s"' % host)
            self.write(filename, 'weight=-10')
            self.write(filename, '+++')
            self.write(filename, "")
            self.write(filename, "## Properties (from configuration file)")
            self.write(filename, "")
            self.write(filename, "Note, items highlighted in RED denote a difference in configuration, not necessarily an error")
            self.write(filename, "")
            self.write(filename, '<table class="pure-table pure-table-bordered">')
            self.write(filename, '<thead>')
            self.write(filename, '<th>Property</th><th>Value</th><th>Default</th>')
            self.write(filename, '</thead>')
            self.write(filename, '<tbody>')
            for j,i in enumerate(self.host_configs[host]):
                def_value = ""
                pvalue = i[1]
                if i[0] in self.default_conf_values:
                    def_value = self.default_conf_values[i[0]]
                    if def_value != pvalue:
                        td_class_color = 'red'
                self.write(filename, '<tr class="%s">' % 'pure-table-odd' if j % 2 != 0 else '<tr>')
                self.write(filename, '<td>%s</td><td class="%s">%s<td style="white-space: nowrap"> %s</td>' % (i[0],td_class_color, pvalue, def_value))
                self.write(filename, '</tr>')
                td_class_color = '' 
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
