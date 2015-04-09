# chkconfig: 35 85 15

PYTHON={python_exe}
CHALMERS={chalmers}

case "$1" in
    start)
        $PYTHON $CHALMERS start --all
        ;;
    stop)
        $PYTHON $CHALMERS stop --all
        ;;
    status)
        $PYTHON $CHALMERS list
        ;;
    restart)
        $PYTHON $CHALMERS restart --all
        start
        ;;
    *)
        echo "Usage:  {{start|stop|status|restart}}"
        exit 1
        ;;
esac
