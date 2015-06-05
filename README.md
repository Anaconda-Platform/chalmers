Superintendent Chalmers
========================

Chalmers is an application that allows its users to monitor and control a
number of processes on ***any*** operating system (Posix and Win32 included)

## Features 

 * **Process control**: Chalmers lets you add remove and monitor programs
 * **System Init**: Chalmers easily allows you to start up your programs at system 
   boot or user login with `chalmers @startup` and `chalmers @login`
 * **Keep Alive**: Chalmers will relaunch your programs if they fail unexpectedly
 * **Logging**: Chalmers will manage store all logs from stdout/stderr and provides easy access with `chalmers log`


[![Binstar Badge](https://anaconda.org/binstar/chalmers/badges/build.svg)](https://anaconda.org/binstar/chalmers/builds)
[![Binstar Badge](https://anaconda.org/binstar/chalmers/badges/version.svg)](https://anaconda.org/binstar/chalmers)
[![Binstar Badge](https://anaconda.org/binstar/chalmers/badges/installer/conda.svg)](https://conda.anaconda.org/binstar)

<center>
    <img src=https://raw.githubusercontent.com/Binstar/chalmers/master/img/chalmers.gif style="margin-left: auto; margin-right: auto;" align="middle" width="100px">
</center>

## Quick Start

#### Adding a Program

This will start the sleep program and keep it running.

    chalmers add --name myprogram -- sleep 1000
    chalmers start myprogram


#### Check the program status

    chalmers list

## Chalmers Program Configuration

To set an option for a program run `chalmers set` eg.

```
chalmers set program-name key1=value1 [key2=value2 ...]
```

See the list below for a list of useful keys


#### Running chalmers on system startup 

This will setup chalmers to start as the current user using the os native init scripts. 
On windows, you can use `runas` instead of `sudo` if you are not administrator. 

    sudo chalmers @startup enable


You can also select the user you want enable at startup:

    sudo chalmers @startup enable --user USER

You will need to start chalmers 

#### Running chalmers on system login
 
Sometimes you may not have root or admin privileges. You can also set up chalmers to run at 
login: 

    chalmers @login enable

#### Turning on and off scripts to be run at login or startup

When chalmers starts at login or startup it will launch all of the programs marked as **on**.

To toggle a single program as on or off run

    chalmers [on|off] myprogram  


### Common Config values:

  * `startsecs`: The time in seconds that the program is assumed to be starting up
    If the program exits before this time it is considered to be spinning
  * `startretries`: The number or times to launch a spinning program
  * `stopwaitsecs`: Wait this long
  * `exitcodes`: A list of exit codes that are accepted as a successful exit 
  * `stopsignal`: The signal to sent to terminate the program. May be an int or string eg: 'SIGTERM' or 15  
    This must be only 'SIGTERM' or 'SIGINT' on win32 platforms.
  * `cwd`: Directory start the program
  * `env.ENVVAR`: Replace `ENVVAR` with the name of the environment variable you want to set.
    eg.
    
    ```
    chalmers set program-name env.PORT=4567
    ```

Log file config values:

 
 * `redirect_stderr`: Direct stderr to the same log file as stdout (default is True)
 * `stdout`: filename to pipe the program's stdout
 * `stderr`: filename to pipe the program's stderr
 * `log_dir`: The base directory to output logs
 * `daemon_log`: filename to pipe the programs control log 
 * env.PYTHONUNBUFFERED: Set this value to 1 if you want are running a 
   python program and want realtime logging 
   See: https://docs.python.org/2/using/cmdline.html#envvar-PYTHONUNBUFFERED 

Posix Only Config values:

  * `umask`: Abbreviation of user mask: sets the file mode creation mask of the current process. 
   See http://en.wikipedia.org/wiki/Umask
  * `user`: User to run the program as. May be a username or UID. This option is only valid when 
    chalmers is run as the root user 

# Example of setting up a server

```
chalmers add --run-later -n server -- python my_server.py
chalmers set server env.PORT=3030
chalmers start server
```

## Chalmers command reference 

| Command | Description |
| ------- | ----------- |
| **Meta Management** | |
| @startup    | enable/disable/status chalmers to run at startup |
| @login    | enable/disable/status chalmers to run at login |
| **Process Control** | |
| add                | Add a program to manage |
| start              | Start a program |
| restart            | Restart a program |
| stop               | Stop running a command |
| off                | Don't run a program on startup or login) |
| on                 | Run a program on startup or login |
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
    Chalmers does this for all platforms with `chalmers service install`.
  * Managing Supervisord config files can be a pain.
    Chalmers allows command line control of the addition and removal of programs with 
    `chalmers add|start|stop|remove`


#### Forever [github.com/nodejitsu/forever](https://github.com/nodejitsu/forever)

  * Forever only supports nodejs applications
  * Forever does not start at system boot.
    Chalmers does this for all platforms with `chalmers service install`.
  * Forever does have windows support, but it can not daemonize windows processes.


#### Honcho [honcho.readthedocs.org](https://honcho.readthedocs.org)

  * Currently chalmers does not support Procfile-based applications (coming soon)

#### Posix sysv-init, upstart, systemd , launchd (osx) and Windows services

  * These utilities require admin privileges to run.  Chalmers does not
  * Chalmers utilizes all of these services by selecting the correct one 
    when `chalmers service install` is run.
  * These utilities require custom wrappers around the scripts that you may need to run.
    Chalmers allows non-root command line control of the addition and removal of 
    programs with `chalmers run|start|stop|remove`


