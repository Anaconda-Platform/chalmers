Superintendent Chalmers
========================

Chalmers is an application that allows its users to monitor and control a 
number of processes on ***any*** operating system (Posix and Win32 included)

## Running chalmers on system boot

    chalmers install-service


## Adding a Program

    chalmers run -- sleep 10

## Chalmers commands

| Command | Description |
| ------- | ----------- |
| edit               | Edit a service definition |
| install-service    | Install chalmers as a service |
| uninstall-service  | Uninstall chalmers as a service |
| service-status     | Check the status of the service |
| list               | List registered programs |
| log                | Show program output |
| manager            | Manage Chalmers programs |
| remove             | Remove a program definition from chalmers |
| run                | Manage a command to run |
| set                | Set a variable in the program definition |
| show               | Show the definition file content |
| start              | Start a program |
| restart            | Restart a program |
| stop               | Stop running a command |
| pause              | Pause program (don't run on system boot) |
| unpause            | Unpause program (run on system boot) |
