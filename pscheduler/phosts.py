from subprocess import Popen, PIPE
import time
from multiprocessing import Pool
import os


class phosts():
    def __init__(self, verbose=True):
        pool = Pool(15)

        self.hostNames = sorted(self.get_host_names())
        self.onlineHosts = []
        self.availableCores = {}

        if len(self.hostNames) > 0:
            temp = pool.map(self.get_online_hosts, self.hostNames)
            for i in range(len(temp)):
                if temp[i][0] is True:
                    self.onlineHosts.append(temp[i][1])
                else:
                    if verbose is True:
                        print (temp[i][1], flush=True)

            temp = pool.map(self.get_available_cores, self.onlineHosts)
            for i in range(len(temp)):
                if temp[i][0] is True:
                    self.availableCores[self.onlineHosts[i]] = temp[i][1]
                else:
                    if verbose is True:
                        print (temp[i][1], flush=True)
        else:
            print ('No host found!', flush=True)

    def launch_subprocess(self, cmd_list, sleep=0):
        time.sleep(sleep)
        process = Popen(cmd_list, stdout=PIPE, stderr=PIPE)
        stdout, stderr = process.communicate()
        return stderr.decode('utf8'), stdout.decode('utf8')

    def get_host_names(self):
        hostfile = os.path.join(os.path.expanduser("~"),
                                '.pscheduler', 'hosts.cfg')
        names = []
        try:
            names = [x.rstrip('\n') for x in open(hostfile).readlines()]
        except:
            print ('ERROR open hostfile %s' % hostfile, flush=True)
        return names

    def get_online_hosts(self, host):
        err, out = self.launch_subprocess([
            'ssh', '-o', 'ConnectTimeout=1',
                   '-o', 'StrictHostKeyChecking=no',
                   host, 'exit'
        ])
        if err == '':
            return True, host
        else:
            return False, "Host %s is not reachable" % host, err

    def get_available_cores(self, host):
        checkcpu_script = os.path.join(os.path.dirname(
            os.path.realpath(__file__)), 'checkCPUusage.py')
        err, out = self.launch_subprocess([
            'ssh', host, 'python', checkcpu_script
        ])
        if err == '':
            return True, out.rstrip('\n')
        else:
            return False, "open cores query failed for host %s" % host, err
