#!/bin/bash

pscheduler service stop
rm -rf ~/.pscheduler
pip uninstall pscheduler -y
pip install .
pscheduler service start
