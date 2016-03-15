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
This plugin provides a top level view of the Eucalyptus cloud volumes

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


class Eucavolumes(sx.plugins.PluginBase):
    """
    Eucalyptus Volumes 
    """

    def __init__(self, pathToPluginReportDir=""):
        """
        @param pathToPluginReportDir: This is the root path to where
        the report files will be written.
        @type pathToPluginReportDir: String
        """
        sx.plugins.PluginBase.__init__(self, "EucaVolumes",
                                       "This plugin provides a list of possible process issues.",
                                       ["Sosreport", "Sysreport"], False, True,
                                       {},
                                       pathToPluginReportDir)
        self.default_property_values = {}
	self.volumes = []

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
            rd = report.getDataFromFile("sos_commands/eucafrontend/euca-describe-vols-v")
            if rd is not None:
                for i in rd:
                    i = i[:-1]  # chop newline
                    if i.startswith("VOLUME"):
                        data = i.split('\t')[1:]  # We don't care about the 'PROPERTY' field
                        # name,size,snap,zone,state,timestamp,standard = data
                        self.volumes.append(tuple(data))
                    # ignore ATTACHEMENT for now

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
        if len(self.volumes) > 0:
            filename = "EucalyptusVolumes.html"
            self.write(filename, "+++")
            self.write(filename, 'title="Volumes"')
            self.write(filename, "weight=-10")
            self.write(filename, 'menu="main"')
            self.write(filename, "+++")
            self.write(filename, "")
            self.write(filename, '<h2> States </h2>')
            state_counts = {}
            for i in self.volumes:
                state_counts[i[4]] = state_counts.setdefault(i[4],0) + 1 
            print state_counts
            self.write(filename, '<table class="pure-table pure-table-bordered">')
            self.write(filename, '<thead>')
            keys = state_counts.keys()
            keys.sort()
            header = "".join(["<th>%s</th>" % i for i in keys])
            self.write(filename, header) 
            self.write(filename, '</thead>')
            self.write(filename, '<tbody>')
            self.write(filename, '<tr>')
            for i in sorted(state_counts):
                self.write(filename, "<td>%s</td>" % state_counts[i])
            self.write(filename, '</tr')
            self.write(filename, '</tbody>')
            self.write(filename, '</table>')
            self.write(filename, '')
            self.write(filename, "<h2> Volumes </h2>")
            self.write(filename, "")
            self.write(filename, '<table class="pure-table pure-table-bordered">')
            self.write(filename, '<thead>')
            self.write(filename, "<th>Name</th><th>Size (in GB)</th><th>Snapshot</th><th>Zone</th><th>State</th><th>Time</th>")
            self.write(filename, '</thead>')
            self.write(filename, '<tbody>')
            for j, i in enumerate(self.volumes):
                self.write(filename, '<tr class="%s">' % 'pure-table-odd' if j % 2 != 0 else '<tr>')
                name,size,snap,zone,state,timestamp,_,_ = i
                self.write(filename, "<td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td>" % (name,size,snap,zone,state,timestamp))
                self.write(filename, '</tr>')
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
