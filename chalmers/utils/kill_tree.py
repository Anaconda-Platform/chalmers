import logging
import psutil

log = logging.getLogger(__name__)

def kill_tree(pid):
    'Kill all processes and child processes'

    try:
        parent = psutil.Process(pid)
    except psutil.NoSuchProcess:
        log.error("NoSuchProcess pid=%s" % pid)
        return

    children = parent.children(recursive=True)

    parent.kill()

    for child in children:
        if child.is_running():
            child.kill()
