import os

hostfile = os.path.join(os.path.expanduser("~"),
                        '.pscheduler', 'hosts.cfg')
hosts = [x.rstrip('\n') for x in open(hostfile).readlines()]
os.system('ssh-keygen -t rsa')
for host in hosts:
    print (host)
    os.system('ssh %s mkdir -p ~/.ssh' % host)
    cmd = "cat ~/.ssh/id_rsa.pub | ssh %s 'cat >> .ssh/authorized_keys'" % host
    os.system(cmd)
