from os.path import expanduser, join, isdir, isfile, dirname, realpath
from os import makedirs, system
from pscheduler import phosts, psub
import sys
import argparse


class Parser(object):

    def __init__(self, job_dir):
        self.jobDir = job_dir
        self.jobdirPath = join(expanduser("~"), self.jobDir, 'jobs')
        if self.make_dir_structure(self.jobDir) is False:
            sys.exit(1)

        parser = argparse.ArgumentParser(
            usage='''pscheduler <subcommand> [<args>]

   service   Core subcommand to control background service
   sub       Submit jobs
   jobs      Monitor running/pending job
   hosts     Get information on available hosts (remote machines)
''')
        parser.add_argument('subcommand', help='Subcommand to run')
        args = parser.parse_args(sys.argv[1:2])
        if not hasattr(self, args.subcommand):
            print ('ERROR: Unrecognized subcommand', flush=True)
            parser.print_help()
            exit(1)
        getattr(self, args.subcommand)()

    def service(self):
        if len(sys.argv) > 2:
            cmd = sys.argv[2]
        else:
            print ("USAGE: pscheduler service {start|stop}", flush=True)
            exit(1)
        if cmd not in ['start', 'stop']:
            print ("USAGE: pscheduler service {start|stop}", flush=True)
            exit(1)
        pidfile = join(expanduser("~"), self.jobDir, 'PROCPID')
        logfile = join(expanduser("~"), self.jobDir, 'DAEMON.log')
        scriptfile = join(expanduser("~"), self.jobDir, 'launch.bash')
        daemon_loc = join(dirname(realpath(__file__)), 'pdaemon.py')
        script = "nohup python %s %s >> %s 2>&1&\necho $! > %s" % (
            daemon_loc, self.jobdirPath, logfile, pidfile)
        if cmd == 'start':
            if isfile(pidfile):
                print ("Process already running!", flush=True)
            else:
                system("touch %s" % pidfile)
                with open(scriptfile, 'w') as OUT:
                    OUT.write(script)
                system('bash %s' % scriptfile)
        else:
            if isfile(pidfile):
                system("kill -9 `cat %s`" % pidfile)
                system("rm %s %s" % (pidfile, scriptfile))
            else:
                print ("Process not running! Nothing to stop.", flush=True)

    def sub(self):
        parser = argparse.ArgumentParser(
            usage='''pscheduler sub [options] "job"
OPTIONS:
    --J/--name       Name of the job
    --o/--outlog     Path of output log file
    --n/--processes  Number of CPU cores required

NOTE: Ensure that job string is within quotes
''')
        parser.add_argument("--name", "-J", default=None)
        parser.add_argument("--outlog", "-o", default=None)
        parser.add_argument("--processes", "-n", type=int, default=1)
        parser.add_argument('job')
        args = parser.parse_args(sys.argv[2:])
        psub.psub(args.job, args.name, args.outlog,
                  args.processes, self.jobdirPath)

    def jobs(self):
        pass

    def hosts(self):
        p = phosts.phosts()
        print ("%d hosts found" % len(p.hostNames), flush=True)
        print ("%d hosts online" % len(p.onlineHosts), flush=True)
        for host in p.onlineHosts:
            if host in p.availableCores:
                print ("%s\t%s" % (host, p.availableCores[host]), flush=True)
        return True

    def make_dir_structure(self, dirname):
        def check_try_make(dirs):
            for d in dirs:
                if not isdir(d):
                    try:
                        makedirs(d)
                    except:
                        print ('FATAL ERROR: Unable to create dir: %s' % d,
                               flush=True)
                        return False
            return True

        home_dir = join(expanduser("~"), dirname)
        jobs_dir = join(home_dir, 'jobs')
        dirs = [home_dir, jobs_dir]
        for sd in ['PEND', 'RUN', 'FINISH', 'SUBSCRIPTS']:
            sub_dir = join(jobs_dir, sd)
            dirs.append(sub_dir)
        if check_try_make(dirs) is False:
            return False
        host_file = join(home_dir, 'hosts.cfg')
        if not isfile(host_file):
            open(join(home_dir, 'hosts.cfg'), 'w').close()
        return True
