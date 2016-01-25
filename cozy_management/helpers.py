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


def cmd_exec(cmd):
    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, close_fds=True)
    p.wait()

    return {
            'error': p.returncode,
            'stdout': p.stdout.readlines(),
            'stderr': p.stderr.readlines()
            }


def array_2_str(array):
    return ''.join(array)


def get_ip_addresses():
    result = cmd_exec('hostname -I')
    return result['stdout'][0].split(' ')[:-1]
