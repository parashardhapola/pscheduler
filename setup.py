from distutils.core import setup

version = open('VERSION').read()

setup(
  name = 'pscheduler',
  packages = ['pscheduler'],
  version = version,
  description = 'A complete multi-remote machine job schedular package in Python',
  author = 'Parashar Dhapola',
  author_email = 'parashar.dhapola@gmail.com',
  url = 'https://github.com/parashardhapola/pscheduler',
  download_url = 'https://github.com/parashardhapola/pscheduler/tarball/%s' % version,
  keywords = ['scheduler', 'python', 'ssh']
)
