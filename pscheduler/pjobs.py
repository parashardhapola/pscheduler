import os
import glob
from terminaltables import AsciiTable
import json
from datetime import datetime
import time


class Pjobs():
    def __init__(self, jobsdir):
        pendloc = os.path.join(jobsdir, 'PEND')
        runloc = os.path.join(jobsdir, 'RUN')
        self.pendFiles = glob.glob("%s/*.json" % pendloc)
        self.runFiles = glob.glob("%s/*.json" % runloc)
        self.header = [
            'Name',
            'Time\nElapsed',
            'Requested\n  Cores',
            'Status',
            'Host',
            'PID',
            'CMD'
        ]
        self.tableData = [list(self.header)]
        self.tableData.extend(self.show_run_jobs())
        self.tableData.extend(self.show_pend_jobs())
        self.table = AsciiTable(self.tableData)
        print (self.table.table)

    def get_elapsed_time(self, t):
        t = datetime.strptime(t, '%Y-%m-%d %H:%M:%S')
        seconds = float(time.time() - time.mktime(t.timetuple()))
        m, s = divmod(seconds, 60)
        h, m = divmod(m, 60)
        return "%d:%02d:%02d" % (h, m, s)

    def show_run_jobs(self):
        data = []
        for runfile in self.runFiles:
            try:
                jobinfo = json.load(open(runfile))
            except FileNotFoundError:
                continue
            try:
                logfile_handle = open("%s.log" % runfile.split('.json')[0])
            except FileNotFoundError:
                pid = '-'
            else:
                try:
                    pid = next(logfile_handle).rstrip('\n')
                except StopIteration:
                    pid = '-'
            run_time = self.get_elapsed_time(jobinfo['BEGTIME'])
            data.append([
                jobinfo['NAME'].split('-')[0],
                run_time,
                jobinfo['NUMPROC'],
                'RUNNING',
                jobinfo['RUNHOST'],
                pid,
                jobinfo['CMD'][-10:]
            ])
        return data

    def show_pend_jobs(self):
        data = []
        for pendfile in self.pendFiles:
            try:
                jobinfo = json.load(open(pendfile))
            except FileNotFoundError:
                continue
            pend_time = self.get_elapsed_time(jobinfo['SUBTIME'])
            data.append([
                jobinfo['NAME'].split('-')[0],
                pend_time,
                jobinfo['NUMPROC'],
                'PENDING',
                '-', '-',
                jobinfo['CMD'][-10:]
            ])
        return data
