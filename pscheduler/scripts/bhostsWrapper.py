#!/usr/bin/env python

import sys
from subprocess import Popen, PIPE
import os


def get_host_names(blacklist):
    names = []
    process = Popen(['bhosts'], stdout=PIPE, stderr=PIPE)
    stdout, stderr = process.communicate()
    err, out = (stderr.decode('utf8'), stdout.decode('utf8'))
    if err != '':
        print('"bhosts" failed.\n%s' % err)
        return False
    for i in out.split('\n')[1:-1]:
        name = i.split(' ')[0]
        if name not in blacklist:
            names.append(name)
    if len(names) > 0:
        return names
    else:
        return False


if __name__ == "__main__":
    if len(sys.argv) > 1:
        blacklist = sys.argv[1].split(',')
    else:
        blacklist = []
    names = get_host_names(blacklist)
    if names is not False:
        hostfile = os.path.join(os.path.expanduser("~"),
                                '.pscheduler', 'hosts.cfg')
        if os.path.isfile(hostfile):
            with open(hostfile, 'w') as handle:
                handle.write("\n".join(names))
            print ('Hostfile "%s" successfully updated!' % hostfile)
        else:
            print ("File %s doesn't exist" % hostfile)
