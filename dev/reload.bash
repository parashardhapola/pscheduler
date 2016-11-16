#!/bin/bash

pscheduler service stop
pip uninstall pscheduler -y
pip install .
rm -rf ~/.pscheduler
pscheduler service start
