import logging
import os

log = logging.getLogger('chalmers.program')

def create_definition(name, command, cwd=os.path.abspath(os.curdir),
                      stdout=None, stderr=None, daemon_log=None, redirect_stderr=None,
                      env=None):

    env = env or {}

    definition = {
                    'name': name,
                    'command': command,
                    'cwd': os.path.abspath(cwd),
                    'env': env,
    }

    if stdout:
        definition['stdout'] = stdout

    if daemon_log:
        definition['daemon_log'] = daemon_log

    if redirect_stderr is not None:
        definition['redirect_stderr'] = redirect_stderr

    if stderr is not None:
        definition['stderr'] = stderr

    return definition

