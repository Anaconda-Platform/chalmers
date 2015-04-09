"""
Install a launchd rule to run at boot 
"""
from __future__ import unicode_literals, print_function

import logging
from subprocess import CalledProcessError, check_output as _check_output, STDOUT
import sys

from chalmers import errors
import pwd
import os

launchd_label = "org.continuum.chalmers"

def label(username):
    if username:
        return '%s.%s' % (launchd_label, username)
    else:
        return launchd_label

log = logging.getLogger('chalmers.service')

def check_output_user(target_user):
    if target_user:
        pw = pwd.getpwnam(target_user)
        env = os.environ.copy()
        env.update({'HOME': pw.pw_dir, 'SHELL': pw.pw_shell, 'USER': pw.pw_name})
        preexec_fn = demote(pw.pw_uid, pw.pw_gid)
        log.info("Changing USER/UID/GID to: %s/%s/%s" % (pw.pw_name, pw.pw_uid, pw.pw_gid))
    else:
        env = os.environ
        preexec_fn = None

    def check_output_inner(command):
        log.info("Running command: %s" % ' '.join(command))
        output = _check_output(command, env=env, cwd='/', preexec_fn=preexec_fn, stderr=STDOUT)
        return output

    return check_output_inner


def get_launchd(target_user):

    check_output = check_output_user(target_user)

    try:
        command = ['launchctl', 'list', label(target_user)]

        return check_output(command)
    except OSError as err:
        raise errors.ChalmersError("Could not access program 'launchctl' required for osx service install")
    except CalledProcessError as err:
        if err.returncode == 1:
            if 'Socket is not connected' in err.output:
                log.error(err.output)
                raise errors.ChalmersError("The user '%s' must be logged in via the osx gui to perform this operation" % target_user)
            return None
        raise


def demote(user_uid, user_gid):
    def result():
        os.setgid(user_gid)
        os.setuid(user_uid)
    return result

def add_launchd(target_user):

    check_output = check_output_user(target_user)

    try:
        chalmers_script = sys.argv[0]
        command = ['launchctl', 'submit', '-l', label(target_user), '--',
                   sys.executable, chalmers_script, 'start', '--all']



        output = check_output(command).strip()
        log.info("launchctl: %s" % output)
    except OSError as err:
        raise errors.ChalmersError("Could not access program 'launchctl' required for osx service install")
    except CalledProcessError as err:
        if err.returncode == 1:
            if 'Socket is not connected' in err.output:
                log.error(err.output)
                raise errors.ChalmersError("The user '%s' must be logged in via the osx gui to perform this operation" % target_user)
            else:
                raise errors.ChalmersError("Chalmers service is already installed")
        raise


def install(args):
    """Create a launchd plist and load as a global daemon"""

    log.info("Adding chalmers launchd plist")
    add_launchd(args.system)
    log.info("All chalmers programs will now run on boot")

def uninstall(args):
    """Uninstall launchd plist for chalmers"""

    target_user = args.system
    check_output = check_output_user(target_user)

    log.info("Removing chalmers plist from launchd")
    try:
        command = ['launchctl', 'remove', label(target_user)]
        output = check_output(command).strip()
    except CalledProcessError as err:
        if err.returncode == 1:
            if 'Socket is not connected' in err.output:
                log.error(err.output)
                raise errors.ChalmersError("The user '%s' must be logged in via the osx gui to perform this operation" % target_user)
            else:
                raise errors.ChalmersError("Chalmers service is not installed")
        raise
    else:
        log.info("Chalmers service has been removed")

def status(args):
    """Check if chalmers will be started at reboot"""

    launchd_lines = get_launchd(args.system)
    if launchd_lines:
        log.info("Chalmers is setup to start on boot")
    else:
        log.info("Chalmers will not start on boot")

