# Eucalyptus Plugins for sxconsole

## Overview:

This project provides eucalytpus cloud specific plugins for the sxconsolue utility. The plugins are written in Python and are designed to provide diagnostic reports for the Eucalyptus cloud.

This plugins work a bit differently than "normal" sxconsole plugins in that they generate content to be processed by the [Hugo](https://gohugo.io/) site generator. Currently there is not a text based output of the reports. 

sxconsole only operates on the input given to it. If two sosreports from a Node Controller are processed for a particular case, then the sxconsole report will only generate data it can glean from those sosreports. Likewise if you feed it sosreports from the CLC, SC, CC and NCs then you will get a better picture of the cloud from the sxconsole report. The plugins should not be written in a way that **requires** dependent sosreports, at least it should run without causing errors.

This project leverages the following technologies:

[sxconsole](https://fedorahosted.org/sx/wiki)
[Hugo](https://gohugo.io)
[Pure](http://purecss.io)

The current list of reports provided:

* Topology - Provides a topology of the provided sosreports.
* Report Mapping - A simple mapping of components to the extracted sosreport
* Configurations - Cloud configuration, and file configurations for hosts
* Timezone Report - All components of the cloud must be in the same timezone.

## Installation:

**Note:** This software is a work in progress.

1) Install sxconsole, check the following page on how to install: (https://fedorahosted.org/sx/wiki)
2) Download and install Hugo, make sure it is in your PATH
3) Lay down the hugo skeleton files to /usr/share/eucalyptus/hugo
4) Copy the plugins into ~/.sx/sxplugins

## Execution:

sxconsole will process sosreports and store them by default into the 'sxarchive' directory in your home directory. An example illustrates the workflow:

```shell
cd /var/tmp/sosreports
# copy sosreports to this directory
ls 
sosreport-1-72NC02-SharedSetup1.000-20150512135727-da25.tar.xz
sosreport-5-14NC02-SharedSetup1.000-20150512135936-b79e.tar.xz
sosreport-5-6NC01-SharedSetup1.000-20150512135434-4c57.tar.xz
sosreport-5-7NC01-SharedSetup1.000-20150512135617-4b47.tar.xz
sosreport-CC-SC01-SharedSetup1.000-20150512134701-1e27.tar.xz
sosreport-CC-SC02-SharedSetup1.000-20150512135209-21a4.tar.xz
sosreport-CLC-Shared-Setup1.000-20150512134250-6951.tar.xz
```

Then execute the sxconsole, enabling the modules you want to run:

```shell
[sgraham@localhost sosreports]$ sxconsole 2010 -E -R /var/tmp/sosreports
STATUS    The list of reports are being analyzed to verify that they are known report types.
INFO      The reports will be extracted to the following directory: /home/sgraham/sxarchive/ereports/2010/2016-03-14_152748
STATUS    Extracting 7 reports.
INFO      This process could take a while on large reports.
STATUS    Extracting the sosreport: /var/tmp/sosreports/sosreport-CLC-Shared-Setup1.000-20150512134250-6951.tar.xz
STATUS    Extracting the sosreport: /var/tmp/sosreports/sosreport-5-6NC01-SharedSetup1.000-20150512135434-4c57.tar.xz
STATUS    Extracting the sosreport: /var/tmp/sosreports/sosreport-CC-SC01-SharedSetup1.000-20150512134701-1e27.tar.xz
STATUS    Extracting the sosreport: /var/tmp/sosreports/sosreport-1-72NC02-SharedSetup1.000-20150512135727-da25.tar.xz
STATUS    Extracting the sosreport: /var/tmp/sosreports/sosreport-5-7NC01-SharedSetup1.000-20150512135617-4b47.tar.xz
STATUS    Extracting the sosreport: /var/tmp/sosreports/sosreport-5-14NC02-SharedSetup1.000-20150512135936-b79e.tar.xz
STATUS    Extracting the sosreport: /var/tmp/sosreports/sosreport-CC-SC02-SharedSetup1.000-20150512135209-21a4.tar.xz
INFO      There was 7 reports extracted to the directory: /home/sgraham/sxarchive/ereports/2010/2016-03-14_152748
INFO      There was 15 plugins enabled.
STATUS    Running setup for plugin: Checksysreport
STATUS    Running setup for plugin: Cluster
STATUS    Running setup for plugin: Gluster
STATUS    Running setup for plugin: Networking
STATUS    Running setup for plugin: OpenSOSReport
STATUS    Running setup for plugin: RHEV
STATUS    Running setup for plugin: SatelliteDebug
STATUS    Running setup for plugin: Storage
STATUS    Running setup for plugin: EucaConfig
STATUS    Running setup for plugin: EucaHugo
STATUS    Running setup for plugin: EucaOrphanedSG
STATUS    Running setup for plugin: EucaProcess
STATUS    Running setup for plugin: EucaTimeZone
STATUS    Running setup for plugin: EucaTopology
STATUS    Running execute for plugin: Checksysreport
ERROR     There was no configuration file for checksysreport, please create the config file: /home/sgraham/.checksysreportrc.
STATUS    Running execute for plugin: EucaConfig
STATUS    Running execute for plugin: EucaHugo
STATUS    Running execute for plugin: EucaOrphanedSG
STATUS    Running execute for plugin: EucaProcess
STATUS    Running execute for plugin: EucaTimeZone
STATUS    Running execute for plugin: EucaTopology
STATUS    Running execute for plugin: EucaTracking
STATUS    Generating report for plugin: Checksysreport
WARNING   There were no cluster nodes found in the list of reports so no report will be generated.
WARNING   There were no gluster peer nodes found in the list of reports so no report will be generated.
STATUS    Generating report for plugin: Networking
STATUS    Generating report for plugin: SatelliteDebug
STATUS    Generating report for plugin: Storage
STATUS    Generating report for plugin: EucaConfig
STATUS    Generating report for plugin: EucaHugo
STATUS    Generating report for plugin: EucaProcess
STATUS    Generating report for plugin: EucaTimeZone
STATUS    Generating report for plugin: EucaTopology
STATUS    Generating report for plugin: EucaTracking
STATUS    Performing action for plugin: OpenSOSReport
STATUS    Performing action for plugin: RHEV
STATUS    Performing action for plugin: EucaConfig
STATUS    Moving directory from /home/sgraham/sxarchive/ereports/2010/2016-03-14_152748/reports/eucaconfig to /home/sgraham/sxarchive/ereports/2010/2016-03-14_152748/reports/content/eucaconfig
STATUS    Performing action for plugin: EucaHugo
STATUS    Writing to: /home/sgraham/sxarchive/ereports/2010/2016-03-14_152748/reports
STATUS    Ran Hugo in /home/sgraham/sxarchive/ereports/2010/2016-03-14_152748/reports
STATUS    Performing action for plugin: EucaOrphanedSG
STATUS    Performing action for plugin: EucaProcess
STATUS    Performing action for plugin: EucaTimeZone
STATUS    Moving directory from /home/sgraham/sxarchive/ereports/2010/2016-03-14_152748/reports/eucatimezone to /home/sgraham/sxarchive/ereports/2010/2016-03-14_152748/reports/content/eucatimezone
STATUS    Performing action for plugin: EucaTopology
STATUS    Moving directory from /home/sgraham/sxarchive/ereports/2010/2016-03-14_152748/reports/eucatopology to /home/sgraham/sxarchive/ereports/2010/2016-03-14_152748/reports/content/eucatopology

EucaProcess plugin File 1:  ~/sxarchive/ereports/2010/2016-03-14_152748/reports/eucaprocess/EucalyptusProcess.html

Details of Report Extraction: 
Compressed Reports Directory: ~/sxarchive/creports/2010/2016-03-14_152748
Extracted Reports Directory:  ~/sxarchive/ereports/2010/2016-03-14_152748
```

Since we can't easily tell Hugo to run last, run sxconsole again on the extracted report directory like so:

```shell
sxconsole -p ~/sxarchive/ereports/2010/2016-03-14_152748/ -e eucahugo
```

Then cd into that directory to run the hugo server:
```shell
cd ~/sxarchive/ereports/2010/2016-03-14_152748/reports 
hugo serve --baseURL="http://192.168.1.41:4000/" --bind="192.168.1.41" --port=4000
```

Now you can launch your favorite browser to view the extracted reports.
