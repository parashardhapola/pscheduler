pscheduler
==========

.. image:: https://travis-ci.org/parashardhapola/pscheduler.svg?branch=master
    :target: https://travis-ci.org/parashardhapola/pscheduler
.. image:: https://img.shields.io/pypi/l/pscheduler.svg
    :target: https://pypi.python.org/pypi/pscheduler
.. image:: https://img.shields.io/pypi/v/pscheduler.svg
    :target: https://pypi.python.org/pypi/pscheduler
.. image:: https://img.shields.io/pypi/wheel/pscheduler.svg
    :target: https://pypi.python.org/pypi/pscheduler
.. image:: https://landscape.io/github/parashardhapola/pscheduler/master/landscape.svg?style=flat
   :target: https://landscape.io/github/parashardhapola/pscheduler/master
   :alt: Code Health


Setup
-----

* This pscheduler service is critical dependent upon the usage of shared filesystem across the remote machines. Setup NFS for all the remote machines.
* Have same login credentials for all the remote machines.
* Basic Linux utilities like *ssh* and *nohup* should be installed on all the remote machines.

Install
-------

**pscheduler** is a Python 3 only module and can be easily installed using pip:

    ``pip install pscheduler``

Configuration
-------------

* Start the service using ``pscheduler service start``. This will create a directory **.pscheduler** under your home directory.
* Edit file **~/.pscheduler/hosts.cfg** and add all the IP addresses/domain aliases of the remote machines in each line. Save and exit. Alternately if you are in an HPC environment and LSF is already installed, then you can use the provided script ``bhostsWrapper.py`` to directly populate the remote machine. You should then edit it to remove the head node machine from the list and any other required host.
* If you have not already setup password-less login into remote machines, then use the provided script ``batchSetupLoginKeys.py`` to set it up. 

Usage
-----

* There are four basic utilities:

    +-------------+-----------------------------------+
    | **service** | start/stop the background service |
    +-------------+-----------------------------------+
    | **hosts**   | get information on remote machines|
    +-------------+-----------------------------------+
    | **sub**     | submit jobs                       |
    +-------------+-----------------------------------+
    | **jobs**    | monitor running/pending job       |
    +-------------+-----------------------------------+

    *See helpfiles of individual subcommands for further details*

* It is critical that the background service is started before the submitting any job

* Examples:

    * Start service: ``pscheduler service start``
    * Submit job: ``pscheduler sub "sleep 10"``

* Pending and running job configuration files are stored under **~/.pscheduler/jobs** in PEND and RUN directory respectively. By default the finished job configuration file containing standard output(JSON format) are stored under **~/.pscheduler/jobs/FINISH**, but users can choose a custom location for this file by using **-o** flag while submitting job and providing the output location path.

* **~/.pscheduler/DAEMON.log** contains the log of the background service. You should have a look at this file to see if any error messages have been thrown.

* Note that pscheduler *will not* will ignore the scheduling by other schedulers and simply launch jobs based on availability of resources (currently only number of CPU cores).

Roadmap for future versions
^^^^^^^^^^^^^^^^^^^^^^^^^^^

* Implement ``jobs`` subcommand
* Job restart in case of resource spike
* Improve code for catching fatal exceptions

HISTORY
^^^^^^^

* 0.0.1:
    * FIRST PRE ALPHA RELEASE
* 0.0.2:
    * CLI CREATED using wrapper.py
    * BHOST wrapper script separated form phosts module
    * Introduced hosts.cfg: A user editable list of hosts
    * Batch script made for creating login keys
    * PSUB now saves in JSON format
    * DEV: Submit to PyPi using python script
    * DEV: Automatic update of version in setup.py
* 0.0.3:
    * Added ``pscheduler`` in scripts for command line invocation
* 0.0.4:
    * Deployment fix
* 0.0.5:
    * Import fix
* 0.0.6:
    * Json fix
* 0.0.7:
    * jobs subcommand implemented
    * phosts doublehost check issue rectified
    * submission process improved in daemon
    * class naming convention changed
    * default host fixed to localhost. passwordless loging into localhost created
    * DEV: Travis CI now being used for testing
* 0.1.0:
	* Rolledback SSH keygen


Contributors
============
Parashar Dhapola (parashar.dhapola@gmail.com)
