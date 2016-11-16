from setuptools import setup, find_packages
import os


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


git_loc = 'https://github.com/parashardhapola/pscheduler'
setup(
    name='pscheduler',
    version=read('VERSION'),
    description=('A pure Python remote job scheduler system'),
    long_description=read('README.rst'),
    author='Parashar Dhapola',
    author_email='parashar.dhapola@gmail.com',
    url=git_loc,
    download_url='%s/tarball/%s' % (git_loc, read('VERSION')),
    license="MIT",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3.5",
        "Topic :: System :: Distributed Computing",
        "Topic :: System :: Networking :: Monitoring"
    ],
    install_requires=[
        'psutil',
        'terminaltables',
    ],
    packages=find_packages(),
    include_package_data=True,
    scripts=['./scripts/batchSetupLoginKeys.py',
             './scripts/bhostsWrapper.py',
             './scripts/pscheduler'],
)
