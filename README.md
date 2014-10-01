Superintendent Chalmers
========================

Chalmers is an application that allows its users to monitor and control a 
number of processes on ***any*** operating system (Posix and Win32 included)

<center>
    <img src=http://mikeydislikesit.files.wordpress.com/2013/05/chalmers1.gif style="margin-left: auto; margin-right: auto;" align="middle" width="100px">
</center>

## Quickstart

#### Running chalmers on system boot

    chalmers install-service


#### Adding a Program

    chalmers run -- sleep 10


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
| pause              | Pause program (don't run on system boot) |
| unpause            | Unpause program (run on system boot) |
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

  * Forever does not start at system boot. 
    Chalmers does this for all platforms with `chalmers install-service`.
  * Forever requires nodejs to be installed
  * 
   
  
#### Honcho [honcho.readthedocs.org](https://honcho.readthedocs.org)

  * Currently chalmers does not support Procfile-based applications (coming soon)

#### Posix init.d and Windows services

  * These utilities require admin privleges to run.  Chalmers does not 
  * These utilities require custom wrappers around the scripts that you may need to run.
    Chalmers allows command line controll of the addition and removal of programs with `chalmers run|start|stop|remove`


