# chkconfig: 35 85 15


PYTHON={python_exe}
CHALMERS={chalmers}
LAUNCH={launch}


case "$1" in
    start)
        $LAUNCH -c "$PYTHON $CHALMERS start --all"
        ;;
    stop)
        $LAUNCH -c "$PYTHON $CHALMERS stop --all"
        ;;
    status)
        $LAUNCH -c "$PYTHON $CHALMERS list"
        ;;
    restart)
        $LAUNCH -c "$PYTHON $CHALMERS restart --all"
        ;;
    *)
        echo "Usage:  {{start|stop|status|restart}}"
        exit 1
        ;;
esac
