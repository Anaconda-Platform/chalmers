Program Configuration
=====================


Setting a config value for a program
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Once you have added a program to chalmers you can set it's environment variables
wit the ``chalmers set`` command.::

  chalmers set program KEY=VALUE
  
Examples
--------

To change the signal used by 'chalmers stop' to shut down a process:

    chalmers set server1 stopsignal=SIGINT

To change an environment variable::

    chalmers set server1 env.PORT=5000


Common Config values
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``startsecs``

  The time in seconds that the program is assumed to be starting up
  If the program exits before this time it is considered to be spinning
  
  *Default*:  10

  
``startretries``
  
  The number or times to try and launch a spinning program

  *Default*:  3

``stopwaitsecs``
 
  Wait this long before concidering a program to be started
  
  *Default*:  3

``exitcodes``

  A list of exit codes that are accepted as a successful exit, e.g.::
  
    chalmers set program exitcodes='[0, 10]'
  
  *Default*:  [0]

``stopsignal`` 
  
  The signal to sent to terminate the program. May be an int or string
  eg: ``SIGTERM`` or ``15``
    
  *Default*:  SIGTERM

``cwd``  
 
  Directory run the command in this directory
  
  *Default*:  The current directory

Environment variables
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``env.*``

  Set environment variables by prefixing them with ``env.`` for example::
  
    chalmers set program env.PORT=80
  

Log file config values
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``log_dir``
 
  The base directory to output logs
 
``redirect_stderr``
  
  Direct stderr to the same log file as stdout

  *Default*:  True

``stdout`` 
  
  filename to pipe the program's stdout
  
``stderr``
  
  filename to pipe the program's stderr
  
``daemon_log`` 
  
  filename to pipe the programs control log
   
``env.PYTHONUNBUFFERED`` 

  Set this value to 1 if you want are running a 
  python program and want realtime logging 
  See: https://docs.python.org/2/using/cmdline.html#envvar-PYTHONUNBUFFERED 

Posix Only Config values
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``umask`` 
  
  Abbreviation of user mask: sets the file mode creation mask of the current process.
   
  .. seealso:: http://en.wikipedia.org/wiki/Umask
  
``user`` 

  User to run the program as. May be a username or UID. 
 
