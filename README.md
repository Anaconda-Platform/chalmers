Superintendent Chalmers
========================

Chalmers is an application that allows its users to monitor and control a 
number of processes on ***any*** operating system (Posix and Win32 included)

## Quickstart

### Running chalmers on system boot

    chalmers install-service


### Adding a Program

    chalmers run -- sleep 10

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
