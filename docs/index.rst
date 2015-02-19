Overview
========

.. Chalmers documentation master file, created by
   sphinx-quickstart on Wed Oct  1 12:45:26 2014.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.


Chalmers is a process control system that has been tested on posix and win32 platforms.

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

Running chalmers on system boot
--------------------------------
 
::

    chalmers service install


Adding a Program
----------------

::

    chalmers add -- sleep 10
    chalmers start sleep


Check the program status
-------------------------

::

    chalmers list



.. toctree::
   :maxdepth: 2
   
   config
   logging


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

