#!/bin/bash

pscheduler service stop
rm -rf ~/.pscheduler
pip uninstall pscheduler -y
pip install .
pscheduler service start
bhostsWrapper.py
grep -v gpu ~/.pscheduler/hosts.cfg | grep -v hpc | grep -v smp1 > ~/.pscheduler/temp.cfg
rm ~/.pscheduler/hosts.cfg
mv ~/.pscheduler/temp.cfg ~/.pscheduler/hosts.cfg
