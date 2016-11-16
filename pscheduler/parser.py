from os.path import expanduser, join, isdir, isfile, dirname, realpath
from os import makedirs, system
from pscheduler import phosts, psub, pjobs
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
        psub.Psub(args.job, args.name, args.outlog,
                  args.processes, self.jobdirPath)

    def jobs(self):
        pjobs.Pjobs(self.jobdirPath)
        return True

    def hosts(self):
        phosts.Phosts()
        return True

    def make_dir_structure(self, dirname):
        def check_try_make(dirs):
            for d in dirs:
                if not isdir(d):
                    try:
                        print ('Creating directory: %s' % d)
                        makedirs(d)
                    except OSError:
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
            with open(host_file, 'w') as OUT:
                OUT.write('localhost')
            print ("INFO: Localhost added to %s" % host_file)
            print ("INFO: Add host IP addresses to %s and remove localhost." %
                   host_file)
            print ("CRITICAL INFO: setup passwordless login for each host.")

            # ssh_dir = join(expanduser("~"), '.ssh')
            # if not isdir(ssh_dir):
            #     makedirs(ssh_dir)
            # rsa_file = join(ssh_dir, 'id_rsa')
            # keys_file = join(ssh_dir, 'authorized_keys')
            # cmds = ['rm -rf %s' % ssh_dir]
            # if not isfile(rsa_file):
            #     cmds.append('ssh-keygen -t rsa -f %s -N ""' % rsa_file)
            # cmds.append('cat %s.pub >> %s' % (rsa_file, keys_file))
            # cmds.append('chmod og-wx %s' % keys_file)
            # options = '-o UserKnownHostsFile=/dev/null ' + \
            #     '-o StrictHostKeyChecking=no'
            # cmds.append('ssh %s localhost exit' % options)
            # temp_script_file = join(expanduser("~"),
            #                         '.temp_keygen_script_file.bash')
            # with open(temp_script_file, 'w') as OUT:
            #     OUT.write("\n".join(cmds))
            # system('bash %s' % temp_script_file)
            # system('rm %s' % temp_script_file)
        return True
