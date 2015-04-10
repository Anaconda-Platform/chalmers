#!/bin/bash
#
# /etc/init.d/{script_name}
#
# chkconfig: 35 85 15
# Handles starting and stopping chalmers.
#
# Author: Continuum Analytics
#
### BEGIN INIT INFO
# Provides:          {{script_name}}
# Required-Start:    $local_fs $remote_fs $network
# Required-Stop:     $local_fs $remote_fs $network
# Default-Start:     3 5
# Default-Stop:      0 1 2 6
# Description:       Provides chalmers service
### END INIT INFO




PYTHON={python_exe}
CHALMERS={chalmers}
LAUNCH="{launch}"


case "$1" in
    start)
        $LAUNCH -c "$PYTHON $CHALMERS start --all"
        logger  -t chalmers "init.d: start exitcode=$?"
        ;;
    stop)
        $LAUNCH -c "$PYTHON $CHALMERS stop --all"
        logger  -t chalmers "init.d: stop exitcode=$?"
        ;;
    status)
        $LAUNCH -c "$PYTHON $CHALMERS list"
        ;;
    restart)
        $LAUNCH -c "$PYTHON $CHALMERS restart --all"
        logger  -t chalmers "init.d: restart exitcode=$?"
        ;;
    *)
        echo "Usage:  {{start|stop|status|restart}}"
        exit 1
        ;;
esac
