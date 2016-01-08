'''
    Some helpers
'''

import os
import pwd


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
