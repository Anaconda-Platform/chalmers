Superintendent Chalmers
========================

Chalmers is an application that allows its users to monitor and control a
number of processes on ***any*** operating system (Posix and Win32 included)

[![Binstar Badge](https://binstar.org/binstar/chalmers/badges/build.svg)](https://binstar.org/binstar/chalmers/builds)
[![Binstar Badge](https://binstar.org/binstar/chalmers/badges/version.svg)](https://binstar.org/binstar/chalmers)
[![Binstar Badge](https://binstar.org/binstar/chalmers/badges/installer/conda.svg)](https://conda.binstar.org/binstar)

<center>
    <img src=https://raw.githubusercontent.com/Binstar/chalmers/master/img/chalmers.gif style="margin-left: auto; margin-right: auto;" align="middle" width="100px">
</center>

## Quickstart

#### Running chalmers on system boot

    chalmers install-service


#### Adding a Program

    chalmers add --name sleep -- sleep 10
    chlamers start sleep


#### Check the program status

    chalmers list


## Chalmers commands

| Command | Description |
| ------- | ----------- |
| **Meta Management** | |
| install-service    | Install chalmers as a service |
| uninstall-service  | Uninstall chalmers as a service |
| service-status     | Check the status of the service |
| manager            | Manage Chalmers programs |
| **Process Control** | |
| run                | Manage a command to run |
| start              | Start a program |
| restart            | Restart a program |
| stop               | Stop running a command |
| off                | Don't run a program on system boot) |
| on                 | Run a program |
| remove             | Remove a program definition from chalmers |
| **Reporting** | |
| list               | List registered programs |
| show               | Show the definition file content |
| log                | Show program output |
| **Updating** | |
| set                | Set a variable in the program definition |
| edit               | Edit a service definition |


## A comparison with other utilities

#### Supervisord [supervisord.org](http://supervisord.org)


  * Supervisord does not run on windows, Chalmers runs on all platforms.
  * Supervisord does not start at system boot.
    Chalmers does this for all platforms with `chalmers install-service`.
  * Managing Supervisord config files can be a pain.
    Chalmers allows command line controll of the addition and removal of programs with `chalmers run|start|stop|remove`


#### Forever [github.com/nodejitsu/forever](https://github.com/nodejitsu/forever)

  * Forever only supports nodejs applications
  * Forever does not start at system boot.
    Chalmers does this for all platforms with `chalmers install-service`.
  * Forever does have windows support, but it can not daemoninze windows processes.


#### Honcho [honcho.readthedocs.org](https://honcho.readthedocs.org)

  * Currently chalmers does not support Procfile-based applications (coming soon)

#### Posix init.d and Windows services

  * These utilities require admin privleges to run.  Chalmers does not
  * These utilities require custom wrappers around the scripts that you may need to run.
    Chalmers allows command line controll of the addition and removal of programs with `chalmers run|start|stop|remove`


