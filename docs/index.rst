Overview
========

.. Chalmers documentation master file, created by
   sphinx-quickstart on Wed Oct  1 12:45:26 2014.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.


Chalmers is an application that allows its users to monitor and control a
number of processes on ***any*** operating system (Posix and Win32 included)

Features
--------

 * **Process control**: Chalmers lets you add remove and monitor programs
 * **System Init**: Chalmers easily allows you to start up your programs at system
   boot or user login with `chalmers @startup` and `chalmers @login`
 * **Keep Alive**: Chalmers will relaunch your programs if they fail unexpectedly
 * **Logging**: Chalmers will manage store all logs from stdout/stderr and provides easy eaccess with `chalmers log`


.. image:: https://binstar.org/binstar/chalmers/badges/build.svg
   :target: https://binstar.org/binstar/chalmers/builds

.. image:: https://binstar.org/binstar/chalmers/badges/version.svg
   :target: https://binstar.org/binstar/chalmers

.. image:: https://binstar.org/binstar/chalmers/badges/installer/conda.svg
   :target: https://conda.binstar.org/binstar

.. image:: https://raw.githubusercontent.com/Binstar/chalmers/master/img/chalmers.gif
   :align: center
   :width: 100px

Quickstart
==========

Adding a Program
----------------

This will start the sleep program and keep it running.::

    chalmers add --name myprogram -- sleep 1000
    chalmers start myprogram


Check the program status
-------------------------

::

    chalmers list



Running chalmers on system startup
===================================

This will setup chalmers to start as the current user using the os native init scripts.
On windows, you can use `runas` instead of `sudo` if you are not administrator.::

    sudo chalmers @startup enable


You can also select the user you want enable at startup::

    sudo chalmers @startup enable --user USER

You will need to start chalmers

Running chalmers on system login
--------------------------------

Sometimes you may not have root or admin privileges. You can also set up chalmers to run at
login::

    chalmers @login enable

Turning on and off scripts to be run at login or startup
--------------------------------------------------------

When chalmers starts at login or startup it will launch all of the programs marked as **on**.

To toggle a single program as on or off run::

    chalmers [on|off] myprogram

Table of Contents
==================


.. toctree::
   :maxdepth: 2

   config
   logging


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

