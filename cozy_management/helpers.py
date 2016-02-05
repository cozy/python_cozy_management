'''
    Some helpers
'''

import os
import pwd
import subprocess


def get_uid(username):
    return int(pwd.getpwnam(username).pw_uid)


def file_rights(filepath, mode=None, uid=None, gid=None):
    '''
        Change file rights
    '''
    file_handle = os.open(filepath, os.O_RDONLY)
    if mode:
        os.fchmod(file_handle, mode)
    if uid:
        if not gid:
            gid = 0
        os.fchown(file_handle, uid, gid)
    os.close(file_handle)


def cmd_exec(cmd, show_output=False):
    if show_output:
        p = subprocess.Popen(cmd, shell=True, close_fds=True)
        stdout, stderr = p.communicate()
    else:
        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, close_fds=True)
        stdout, stderr = p.communicate()

        return {
                'error': p.returncode,
                'stdout': stdout,
                'stderr': stderr
                }


def array_2_str(array):
    return ''.join(array)


def get_ip_addresses():
    result = cmd_exec('hostname -I')
    return result['stdout'].split(' ')[:-1]
