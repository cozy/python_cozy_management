'''
    Backup
'''

import os
import time

from . import helpers

BACKUPS_PATH = '/var/lib/cozy/backups'


def backup():
    '''
        Backup a Cozy
    '''
    if not os.path.isdir(BACKUPS_PATH):
        print 'Need to create {}'.format(BACKUPS_PATH)
        os.makedirs(BACKUPS_PATH, 0700)
    timestamp = time.strftime("%Y-%m-%d-%H-%M-%S", time.gmtime())
    cmd = 'tar cvzf {}/cozy-{}.tgz'
    cmd += ' --exclude stack.token'
    cmd += ' --exclude couchdb.login'
    cmd += ' --exclude self-hosting.json'
    cmd += ' /etc/cozy /usr/local/var/cozy /var/lib/couchdb/cozy.couch'
    cmd = cmd.format(BACKUPS_PATH, timestamp)
    helpers.cmd_exec(cmd, show_output=True)


def restore(backup_file):
    '''
        Restore a Cozy
        backup_file: path to .tar.gz
    '''
    if not os.path.isfile(backup_file) and not os.path.islink(backup_file):
        print 'Missing backup file: {}'.format(backup_file)
    else:
        print 'Restore Cozy:'
        cmd = 'tar xvzf {} -C /'.format(backup_file)
        helpers.cmd_exec(cmd, show_output=True)
