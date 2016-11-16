#!/bin/bash

pscheduler service stop
pip uninstall pscheduler -y
pip install .
rm -rf ~/.pscheduler/jobs ~/.pscheduler/DAEMON.log
pscheduler service start
