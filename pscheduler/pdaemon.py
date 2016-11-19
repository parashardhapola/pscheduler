import glob
from pscheduler import phosts
import time
import os
import datetime
from subprocess import Popen, PIPE
import json
import sys


def get_timestamp():
    return '{:%Y-%m-%d %H:%M:%S}'.format(
        datetime.datetime.now())


def launch_subprocess(cmd_list, sleep=0):
    time.sleep(sleep)
    process = Popen(cmd_list, stdout=PIPE, stderr=PIPE)
    stdout, stderr = process.communicate()
    return stderr.decode('utf8'), stdout.decode('utf8')


class Job():
    def __init__(self, pendfile, locations):
        self.pendFile = pendfile
        self.locations = locations
        self.uid = self._get_uid()
        self.info = self.read_pend_file()

        self.runFile = None
        self.scriptFile = None
        self.logFile = None

    def get_requested_cores(self):
        print ("%s: %d cores have been requested by the job" %
               (get_timestamp(), self.info['NUMPROC']))
        return int(self.info['NUMPROC'])

    def _get_uid(self):
        try:
            uid = self.pendFile.split('/')[-1].split('.')[0]
        except IndexError:
            print ("%s: Unable to get UID form file %s" % (
                get_timestamp(), self.pendFile))
            uid = False
        return uid

    def _read_pend_file(self):
        try:
            retval = json.load(open(self.pendFile))
        except JSONDecodeError:
            print ("%s: Unable to read JSON file %s" % (
                get_timestamp(), self.pendFile))
            retval = False
        return retval

    def _make_run_file(self):
        self.info['BEGTIME'] = self.get_timestamp()
        self.runFile = "%s/%s.json" % (self.locations['RUN'], self.uid)
        try:
            with open(self.runFile, 'w') as OUT:
                json.dump(self.info, OUT, indent=2)
            return True
        except (TypeError, FileNotFoundError):
            print ("%s: Unable to write out run file %s" % (
                get_timestamp(), self.runFile))
            return False

    def _make_script_file(self):
        try:
            script = "#!/bin/bash\n\necho $$;\ncd %s;\n%s\n" % (
                self.info['CWD'], self.info['CMD'])
        except AttributeError:
            print ("%s: Malformed CWD or CMD in JSON file %s" % (
                get_timestamp(), self.pendFile))
            return False
        self.scriptFile = "%s/%s.bash" % (
            self.locations['SUBSCRIPTS'], self.uid)
        try:
            with open(self.scriptFile, 'w') as OUT:
                OUT.write(script)
        except FileNotFoundError:
            print ("%s: Unable to write out script file %s" % (
                get_timestamp(), self.scriptFile))
            return False
        else:
            os.system("chmod 777 %s" % self.scriptFile)
        return True

    def _make_log_file(self):
        self.logFile = "%s/%s.log" % (self.locations['RUN'], self.uid)
        try:
            FH = open(self.logFile, 'w')
            FH.close()
        except FileNotFoundError:
            print ("%s: Unable to create log file %s" % (
                get_timestamp(), self.logFile))
            return False
        return True

    def _delete_file(self, filename):
        os.system("rm -f %s" % filename)
        return True

    def _pre_sub_check(self):
        if self._make_script_file() is True:
            if self._make_run_file() is True:
                if self._make_log_file() is True:
                    self._delete_file(self.pendFile)
                    return True
                else:
                    self._delete_file(self.scriptFile)
                    self._delete_file(self.runFile)
            else:
                self._delete_file(self.scriptFile)
        return False

    def submit(self, host):
        try:
            self.info['RUNHOST'].append(host)
        except AttributeError:
            print ("%s: Malformed RUNHOST in JSON file %s" % (
                get_timestamp(), self.pendFile))
            return False
        if self._pre_sub_check() is True:
            sub = "ssh %s nohup %s </dev/null > %s 2>&1 &" % (
                host, self.scriptFile, self.logFile)
            os.system(sub)
            print ("%s: %s job submitted" % (
                get_timestamp(), self.info['NAME']))
            return True
        else:
            self.info['RUNHOST'] = self.info['RUNHOST'][:-1]
            return False

    def _get_pid(self):
        if not os.path.isfile(self.logFile):
            print ("%s: Failed to find log file %s" % (
                get_timestamp(), self.logFile))
            return None
        else:
            data = open(self.logFile).readlines()
            try:
                pid = data[0].rstrip('\n')
            except IndexError:
                print ('%s: PID not assigned for %d' % (
                    get_timestamp(), self.info['NAME']))
                return None
            try:
                pid = int(pid)
            except ValueError:
                print ('%s: PID not returned for job %d. Got message: %s' % (
                    get_timestamp(), self.info['NAME'], pid))
                return False  # rollback from here
        return pid

    def check_status(self):
        pid = self._get_pid()
        if pid is None:
            return None
        elif pid is False:
            return False  # unrecoverable error initiate rollback
        else:
            check_cmd = ['ssh', self.info['RUNHOST'][-1],
                         "ps x | grep %s" % pid]
            _, out = launch_subprocess(check_cmd)
            complete = True
            for l in out.split('\n'):
                if l.rstrip('\n').split(' ')[0] == pid:
                    complete = False
                    break
            if complete is True:
                print ("%s: Job completed on host %s" % (
                    get_timestamp(), self.info['RUNHOST'][-1]))
            return complete

    def _purge(self):
        try:
            output = open(self.logFile).readlines()[1:]
        except IndexError:
            output = 'None'
        self._delete_file(self.scriptFile)
        self._delete_file(self.runFile)
        self._delete_file(self.logFile)
        return output

    def rollback(self):
        _ = self._purge()
        try:
            with open("%s.json" % self.pendFile, 'w') as OUT:
                json.dump(self.info, OUT, indent=2)
        except FileNotFoundError:
            return False
        return True

    def _make_out_file(self):
        outfile = "%s/%s_%s.log" % (self.info['OUTLOC'].rstrip('/'),
                                    self.uid, self.info['NAME'])
        try:
            with open(outfile, 'w') as OUT:
                json.dump(self.info, OUT, indent=2)
        except FileNotFoundError:
            print ("%s: Unable to create output file %s" % (
                   get_timestamp(), outfile))
            return False
        print ("%s: Job %s completed" % (
            get_timestamp(), self.info['NAME']))
        return True

    def clean(self):
        self.info['OUTPUT'] = self._purge()
        self.info['FINTIME'] = get_timestamp()
        self._make_out_file()  # FIXME
        return True


class Pdaemon():
    def __init__(self, jobs_dir):
        self.sleepTime = 2
        self.jobsDir = jobs_dir
        self.locations = {}
        for sd in ['PEND', 'RUN', 'SUBSCRIPTS']:
            self.locations[sd] = os.path.join(self.jobsDir, sd)
        self.jobsList = []
        self.run()

    def update_hosts(self):
        hosts_cores_dict = phosts.Phosts(verbose=False).availableCores
        cores = map(int, hosts_cores_dict.values())
        if len(cores) > 0:
            print ("%s: Total %d available cores found!" %
                   (get_timestamp(), sum(cores)), flush=True)
        return hosts_cores_dict

    def acquire_jobs(self):
        json_files = glob.glob("%s/*.json" % self.locations['PEND'])
        if len(json_files) > 0:
            print ("%s: %d job files found" % (
                get_timestamp(), len(jobfiles)), flush=True)
        jobs = []
        for fn in json_files:
            jobs.append(Job(fn, self.locations))  # <- instantiating Job class
        return jobs

    def get_suitable_host(self, hosts_info, requested_cores):
        for host in hosts_info:
            cores = int(hosts_info[host])
            if cores < 3:
                continue
            if cores > requested_cores + 1:
                print ("%s: Submitting to %s: has %d free cores" %
                       (get_timestamp(), host, cores), flush=True)
                return host
        return False

    def submit_jobs(self):
        jobs = self.acquire_jobs()
        hosts_info = self.update_hosts()
        for job in jobs:
            requested_cores = job.get_requested_cores()  # <- Jobs method
            suitable_host = get_suitable_host(self, hosts_info,
                                              requested_cores)
            if suitable_host is False:
                continue
            else:
                job.submit(suitable_host)  # <- Jobs method
                hosts_info[host] = int(hosts_info[host]) - requested_cores
        return jobs

    def clean_jobs(self):
        clean_index = []
        for i in range(len(self.jobsList)):
            check_status = self.jobsList[i].check_status()  # <- Jobs method
            if check_status is True:
                self.jobsList[i].clean()  # <- Jobs method
                # Create outfile error silent but logged
                clean_index.append(i)
            elif check_status is False:  # Could also be None which is no probs
                self.jobsList[i].rollback()
                clean_index.append(i)
        return [self.jobsList[i] for i in range(len(self.jobsList))
                if i not in clean_index]

    def run(self):
        print ("%s: --------DAEMON STARTED--------" % get_timestamp(),
               flush=True)
        while True:
            self.jobsList.extend(self.submit_jobs())
            self.jobsList = self.clean_jobs()
            time.sleep(self.sleepTime)
        return None


if __name__ == "__main__":
    try:
        jobs_dir = sys.argv[1]
    except IndexError:
        print ('Please provide jobs directory path to pdaemon', flush=True)
        exit(1)
    else:
        Pdaemon(jobs_dir)
