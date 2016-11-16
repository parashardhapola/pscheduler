from subprocess import Popen, PIPE
import time
from multiprocessing import Pool
import os
from terminaltables import AsciiTable


class Phosts():
    def __init__(self, verbose=True):
        pool = Pool(15)

        self.hostNames = sorted(self.get_host_names())
        self.availableCores = {}

        if len(self.hostNames) > 0:
            temp = pool.map(self.get_available_cores, self.hostNames)
            for i in range(len(temp)):
                if temp[i][0] is True:
                    self.availableCores[self.hostNames[i]] = temp[i][1]
                else:
                    if verbose is True:
                        print (temp[i][1], flush=True)
            if verbose is True:
                table_data = [['Host\nname', '# available\n   cores']]
                table_data.extend([[x, str(self.availableCores[x])]
                                   for x in self.hostNames
                                   if x in self.availableCores])
                table = AsciiTable(table_data)
                print (table.table)
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
        except FileNotFoundError:
            print ('ERROR open hostfile %s' % hostfile, flush=True)
        return names

    def get_available_cores(self, host):
        checkcpu_script = os.path.join(os.path.dirname(
            os.path.realpath(__file__)), 'checkCPUusage.py')
        err, out = self.launch_subprocess([
            'ssh', '-o', 'ConnectTimeout=3',
                   '-o', 'StrictHostKeyChecking=no',
                   '-o', 'BatchMode=yes',
                   host, 'python', checkcpu_script
        ])
        if err == '':
            return True, out.rstrip('\n')
        else:
            return False, "Host %s is not reachable" % host, err
