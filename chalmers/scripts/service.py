import sys, os
import getpass
import traceback
import time

def main():

    AllUsersProfile = os.environ.get('AllUsersProfile', 'C:\\ProgramData')
    user= getpass.getuser().rsplit('\\',1)[-1]
    logfile = os.path.join(AllUsersProfile, '%s-chalmers-service-log.txt' % getpass.getuser())

    try:
        logfd = open(logfile, 'a', 1)
    except:
        # I guess we will have to leave it up to the windows event log
        traceback.print_exc()
    else:
        sys.stdout = sys.stderr = logfd

    print '---'
    print "Starting Chalmers Service", time.ctime()
    sys.stdout.flush()

    from chalmers.windows.chalmers_service import ChalmersService
    import servicemanager
    servicemanager.Initialize(None, None)
    servicemanager.PrepareToHostSingle(ChalmersService)
    servicemanager.StartServiceCtrlDispatcher()


if __name__ == "__main__":
    main()
