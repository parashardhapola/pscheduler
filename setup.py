from setuptools import setup, find_packages

version = open('VERSION').read()
desc = 'A pure Python remote job scheduler system'
url = 'https://github.com/parashardhapola/pscheduler/tarball/%s' % version
classifiers = [
    'Development Status :: 3 - Alpha',
    'Environment :: Console',
    'License :: OSI Approved :: MIT License',
    'Natural Language :: English',
    'Operating System :: POSIX :: Linux',
    'Programming Language :: Python :: 3.5',
    'Topic :: System :: Distributed Computing',
    'Topic :: System :: Networking :: Monitoring'
]


setup(
    name='pscheduler',
    version=version,
    description=desc,
    author='Parashar Dhapola',
    author_email='parashar.dhapola@gmail.com',
    url='https://github.com/parashardhapola/pscheduler',
    download_url=url,
    keywords=['scheduler'],
    license="MIT",
    classifiers=classifiers,
    install_requires=['psutil'],
    packages=find_packages(),
    include_package_data=True,
    scripts=['./scripts/batch_setup_login_keys.py',
             './scripts/bhostsWrapper.py'],
)
