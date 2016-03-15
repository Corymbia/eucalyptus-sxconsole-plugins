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
This plugin processes the output of other eucalyptus sxconsole
plugins. It runs the Hugo command to generate a website.

Skeleton files are expected to be in: /usr/share/eucalyptus/hugo

The plugin can be placed in the directory: $HOME/.sx/sxplugins/
$ cp demo.py $HOME/.sx/sxplugins/

It will need to be enabled.

@version   :  1.0 
"""
import os
import shutil
import logging
import subprocess

import sx
import sx.plugins
from sx.logwriter import LogWriter


class Eucahugo(sx.plugins.PluginBase):
    """
    Eucalyptus HTML Generation using Hugo
    """

    def __init__(self, pathToPluginReportDir=""):
        """
        @param pathToPluginReportDir: This is the root path to where
        the report files will be written.
        @type pathToPluginReportDir: String
        """
        sx.plugins.PluginBase.__init__(self, "EucaHugo",
                                       "This plugin processes reports.",
                                       ["Sosreport", "Sysreport"], False, True,
                                       {"serve": "Launches Hugo with the 'serve' command. [off]",
                                        "port": "Port to use when serving pages. [4000]",
                                        "skelfiles": "Files where Hugo defaults are located: [/usr/share/eucalyptus/hugo]"
                                        },
                                       pathToPluginReportDir)
        self.setOptionValue("serve", 'off')
        self.setOptionValue("port", '4000')
        self.setOptionValue("skelfiles", '/usr/share/eucalyptus/hugo')

        self.default_hostname = "192.168.1.41" # sxconsole doesn't parse the options clean enough to allow passing ips addrs.
        #self.setOptionValue("hostname", '127.0.0.1')

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

    def action(self):
        """
        This function performs some external task such as opening web
        browser or file viewer to view a file.
        """
        # Always print this message if you going to call this function
        # so that logging is notified that this function has been called.
        message = "Performing action for plugin: %s" % (self.getName())
        logging.getLogger(sx.MAIN_LOGGER_NAME).status(message)

        report_dir = self.getPathToPluginReportDir()
        h, _ = os.path.split(report_dir)
        report_path = None
        if os.path.isdir(h):
            report_path = h
        else:
            logging.getLogger(sx.MAIN_LOGGER_NAME).status("Failed to find a report directory: %s" % h)
            return -1

        # Lay down files needed by Hugo to build a proper "site"
        hugo_files = self.getOptionValue('skelfiles')
        for fname in os.listdir(hugo_files):
            src_file = os.path.join(hugo_files, fname)
            dst_file = os.path.join(report_path, fname)
            if os.path.isdir(src_file):
                if not os.path.exists(dst_file):
                    shutil.copytree(src_file, dst_file)
            else:
                shutil.copy2(src_file, dst_file)

        logging.getLogger(sx.MAIN_LOGGER_NAME).status("Writing to: %s" % report_path)
        command = ["hugo",'-s',report_path,'-d', os.path.join(report_path,"public")] 
        task = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        (stdout, stderr) = task.communicate()
        if task.returncode == 0:
            logging.getLogger(sx.MAIN_LOGGER_NAME).status("Ran Hugo in %s" % report_path)
            if self.getOptionValue("serve") == "on":
                port = self.getOptionValue("port")
                hostname = self.default_hostname
                logging.getLogger(sx.MAIN_LOGGER_NAME).status("Launching Hugo server on host: %s port: %s, dir: %s hit Ctrl-C to stop" % (hostname, port, report_path))
                command = ["hugo", "serve", '--bind="%s"' % hostname, 
                           '--port=%s' % port,
                           "-s",os.path.join(report_path, "public")]
                logging.getLogger(sx.MAIN_LOGGER_NAME).status("Command: %s", " ".join(command))
                task = subprocess.Popen(command, cwd=report_path,
                                        stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                (stdout,stderr) = task.communicate()
                logging.getLogger(sx.MAIN_LOGGER_NAME).status("HMMM")
                logging.getLogger(sx.MAIN_LOGGER_NAME).status(stdout)
                # will wait until Ctrl-C is hit.
        else:
            logging.getLogger(sx.MAIN_LOGGER_NAME).status("Failed to run Hugo")
            logging.getLogger(sx.MAIN_LOGGER_NAME).status(stderr)
            logging.getLogger(sx.MAIN_LOGGER_NAME).status(stdout)
