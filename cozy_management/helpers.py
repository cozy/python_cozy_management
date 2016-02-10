'''
    Some helpers
'''

import os
import pwd
import time
import requests
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
        return p.returncode
    else:
        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE, close_fds=True)
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


def wait_http(url, ok_message, interval=10):
        couchdb_status = False
        while not couchdb_status:
            try:
                requests.get(url)
                couchdb_status = True
                print ok_message
            except requests.exceptions.ConnectionError, e:
                print e
                time.sleep(interval)


def wait_couchdb(interval=10):
    wait_http('http://127.0.0.1:5984/', 'CouchDB OK', interval)


def wait_cozy_controller(interval=10):
    wait_http('http://127.0.0.1:9002/', 'Cozy controller OK', interval)


def wait_cozy_datasytem(interval=10):
    wait_http('http://127.0.0.1:9101/', 'Cozy data sytem OK', interval)


def wait_cozy_home(interval=10):
    wait_http('http://127.0.0.1:9103/', 'Cozy home OK', interval)


def wait_cozy_proxy(interval=10):
    wait_http('http://127.0.0.1:9104/', 'Cozy proxy OK', interval)


def wait_cozy_stack(interval=10):
    wait_couchdb(interval)
    wait_cozy_controller(interval)
    wait_cozy_datasytem(interval)
    wait_cozy_home(interval)
    wait_cozy_proxy(interval)
