import os
import datetime
import uuid
import json


class Psub():
    def __init__(self, cmd, name, outloc, proc, job_dir):
        self.pendLoc = os.path.join(job_dir, 'PEND')
        uid = uuid.uuid1()
        if name is None:
            name = str(uid)
        if outloc is None:
            outloc = os.path.join(job_dir, 'FINISH')
        pend_dict = {
            'SUBTIME': self.get_timestamp(),
            'CWD': os.getcwd(),
            'NAME': name,
            'OUTLOC': outloc,
            'NUMPROC': proc,
            'CMD': cmd,
            'RUNHOST': [],
            'BEGTIME': '',
            'OUTPUT': '',
            'FINTIME': ''
        }
        with open("%s/%s.json" % (self.pendLoc, uid), 'w') as OUT:
            json.dump(pend_dict, OUT, indent=2)

    def get_timestamp(self):
        return '{:%Y-%m-%d %H:%M:%S}'.format(
            datetime.datetime.now())
