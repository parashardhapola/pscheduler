import glob
from pscheduler import phosts
import time
import os
import datetime
from subprocess import Popen, PIPE
import json
from collections import OrderedDict
import sys


class pdaemon():
    def __init__(self, jobs_dir):
        self.sleepTime = 10
        self.jobsDir = jobs_dir
        self.locations = {}
        for sd in ['PEND', 'RUN', 'SUBSCRIPTS']:
            self.locations[sd] = os.path.join(self.jobsDir, sd)
        self.run()

    def update_hosts(self):
        return phosts.Phosts(verbose=False).availableCores

    def acquire_jobs(self):
        json_files = glob.glob("%s/*.json" % self.locations['PEND'])
        return json_files

    def get_timestamp(self):
        return '{:%Y-%m-%d %H:%M:%S}'.format(
            datetime.datetime.now())

    def submit_job(self, host, fn):
        jobinfo = json.load(open(fn), object_pairs_hook=OrderedDict)
        uid = fn.split('/')[-1].split('.')[0]
        script = "#!/bin/bash\n\necho $$;\ncd %s;\n%s\n" % (
            jobinfo['CWD'], jobinfo['CMD'])
        script_file = "%s/%s.bash" % (self.locations['SUBSCRIPTS'], uid)
        with open(script_file, 'w') as OUT:
            OUT.write(script)
        os.system("chmod 777 %s" % script_file)

        runfn = "%s/%s.json" % (self.locations['RUN'], uid)
        jobinfo['RUNHOST'] = host
        jobinfo['BEGTIME'] = self.get_timestamp()
        with open(runfn, 'w') as OUT:
            json.dump(jobinfo, OUT, indent=2)
        os.system("rm %s" % fn)  # delete json in PEND

        logfn = "%s/%s.log" % (self.locations['RUN'], uid)
        sub = "ssh %s nohup %s </dev/null > %s 2>&1 &" % (
            host, script_file, logfn)
        os.system(sub)
        print ("%s: %s job submitted" % (
            self.get_timestamp(), jobinfo['NAME']), flush=True)

        return True

    def launch_subprocess(self, cmd_list, sleep=0):
        time.sleep(sleep)
        process = Popen(cmd_list, stdout=PIPE, stderr=PIPE)
        stdout, stderr = process.communicate()
        return stderr.decode('utf8'), stdout.decode('utf8')

    def clean_jobs(self):
        submitted_jobs = glob.glob("%s/*.json" % self.locations['RUN'])
        if len(submitted_jobs) > 0:
            print ("%s: %d jobs in RUN dir" % (
                self.get_timestamp(), len(submitted_jobs)), flush=True)
        for runfn in submitted_jobs:
            uid = runfn.split('/')[-1].split('.')[0]
            logfn = "%s/%s.log" % (self.locations['RUN'], uid)
            if os.path.isfile(logfn):
                try:
                    data = open(logfn).readlines()
                    pid = data[0].rstrip('\n')
                except:
                    continue
                jobinfo = json.load(open(runfn))
                check_cmd = ['ssh', jobinfo['RUNHOST'], "ps x | grep %s" % pid]
                err, out = self.launch_subprocess(check_cmd)
                complete = True
                for l in out.split('\n'):
                    if l.rstrip('\n').split(' ')[0] == pid:
                        complete = False
                        break
                if complete is True:
                    try:
                        output = data[1:]
                    except:
                        output = ''

                    script_file = "%s/%s.bash" % (self.locations['SUBSCRIPTS'],
                                                  uid)
                    os.system("rm %s %s %s" % (script_file, logfn, runfn))

                    jobinfo['OUTPUT'] = output
                    jobinfo['FINTIME'] = self.get_timestamp()
                    outfile = "%s/%s_%s.log" % (jobinfo['OUTLOC'].rstrip('/'),
                                                uid, jobinfo['NAME'])
                    with open(outfile, 'w') as OUT:
                        json.dump(jobinfo, OUT, indent=2)
                    print ("%s: Job %s completed" % (
                        self.get_timestamp(), jobinfo['NAME']), flush=True)
        return True

    def run(self):
        print ("%s: --------DAEMON STARTED--------" % self.get_timestamp(),
               flush=True)
        deep_sleep_mode = True
        while True:
            jobfiles = self.acquire_jobs()
            if len(jobfiles) > 0:
                deep_sleep_mode = False
                print ("%s: %d job files found" % (
                    self.get_timestamp(), len(jobfiles)), flush=True)
                print ("%s: Updating hosts core info" %
                       self.get_timestamp(), flush=True)
                hosts = self.update_hosts()
                submitted_jobs = []
                for njob in range(len(jobfiles)):
                    jobfile = jobfiles[njob]
                    requested_cores = int(json.load(open(
                        jobfile))['NUMPROC'])
                    for host in hosts:
                        cores = int(hosts[host])
                        print ("%s: %s has %d free cores" %
                               (self.get_timestamp(), host, cores), flush=True)
                        if cores > requested_cores:
                            self.submit_job(host, jobfile)
                            submitted_jobs.append(njob)
                            break
                jobfiles = [jobfiles[x] for x in range(len(jobfiles))
                            if x not in submitted_jobs]
                print ("%s: %d outstanding jobs to be submitted." %
                       (self.get_timestamp(), len(jobfiles)))
            self.clean_jobs()
            if len(jobfiles) == 0:
                if deep_sleep_mode is False:
                    print ("%s: Sleeping" % self.get_timestamp(), flush=True)
                    deep_sleep_mode = True
                time.sleep(self.sleepTime)
        return None


if __name__ == "__main__":
    try:
        jobs_dir = sys.argv[1]
    except:
        print ('Please provide jobs directory path to pdaemon', flush=True)
        exit(1)
    else:
        pdaemon(jobs_dir)
