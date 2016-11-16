from setuptools import setup, find_packages

version = open('VERSION').read()
git_loc = 'https://github.com/parashardhapola/pscheduler'
setup(
    name='pscheduler',
    version=version,
    description='A pure Python remote job scheduler system',
    author='Parashar Dhapola',
    author_email='parashar.dhapola@gmail.com',
    url=git_loc,
    download_url='%s/tarball/%s' % (git_loc, version),
    license="MIT",
    categories=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3.5',
        'Topic :: System :: Distributed Computing',
        'Topic :: System :: Networking :: Monitoring'
    ],
    install_requires=['psutil', 'terminaltables'],
    packages=find_packages(),
    include_package_data=True,
    scripts=['./scripts/batchSetupLoginKeys.py',
             './scripts/bhostsWrapper.py',
             './scripts/pscheduler'],
)
