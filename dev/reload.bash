#!/bin/bash

pscheduler service stop
rm -rf ~/.pscheduler ~/.ssh
pip uninstall pscheduler -y
pip install .
pscheduler service start
