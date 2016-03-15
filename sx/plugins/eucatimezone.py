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

@author    :  Steven Graham 
@contact   :  steven.graham@hpe.com
@version   :  1.0 
"""
import os
import shutil
import logging

import sx
import sx.plugins
from sx.logwriter import LogWriter

class Eucatimezone(sx.plugins.PluginBase):
    """
    Eucalyptus SosReport Timezone  
    """

    def __init__(self, pathToPluginReportDir=""):
        """
        @param pathToPluginReportDir: This is the root path to where
        the report files will be written.
        @type pathToPluginReportDir: String
        """
        sx.plugins.PluginBase.__init__(self, "EucaTimeZone",
                                       "This plugin verifies that the timezones are correct across the given sosreports.",
                                       ["Sosreport", "Sysreport"], False, True,
                                       {},
                                       pathToPluginReportDir)
        self.dates_by_tz = {}

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

        for report in reports:
            po = report.getDataFromFile('date')
            #self.dates_by_host[report.getHostname()] = po[0].rstrip()  # the first line is the header...
            tz = po[0].rstrip().split()[-2]
            # key: tz, value, set of hostname,datestring tuples
            self.dates_by_tz.setdefault(tz,set()).add((report.getHostname(),po[0].rstrip()))

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
        filename = "EucalyptusTimezone.md"
        self.write(filename, "+++")
        self.write(filename, 'title="Timezone Report"')
        self.write(filename, 'menu="main"')
        self.write(filename, "+++")
        self.write(filename, "")
        if len(self.dates_by_tz) > 1:
            self.write(filename, '<font color="red">An error has been detected, all timzeones should be the same.')
            self.write(filename, 'There are %s different timezones in the cloud, there should be 1' % len(self.dates_by_tz))
            self.write(filename, "")
            self.write(filename, 'Please verify and fix the timzone on the set of hosts that are not compliant.')
            self.write(filename, '</font>')
        for tz in self.dates_by_tz:
            self.write(filename, '<h2> Timezone: %s </h2>' % tz)
            self.write(filename, '<table class="pure-table pure-table-bordered">')
            self.write(filename, '<thead>')
            self.write(filename, '<th>Hostname</th><th>Date</th>')
            self.write(filename, '</thead>')
            self.write(filename, '<tbody>')
            for d,t in self.dates_by_tz[tz]:
                self.write(filename, '<tr>')
                self.write(filename, '<td>%s</td><td>%s</td>' % (d,t))
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
        message = "Performing action for plugin: %s" % (self.getName())
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

