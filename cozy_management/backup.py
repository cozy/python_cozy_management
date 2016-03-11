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
    print 'Backup file: {}/cozy-{}.tgz'.format(BACKUPS_PATH, timestamp)


def restore(backup_file):
    '''
        Restore a Cozy
        backup_file: path to .tar.gz
    '''
    if not os.path.isfile(backup_file) and not os.path.islink(backup_file):
        print 'Missing backup file: {}'.format(backup_file)
    else:
        print 'Restore Cozy:'
        cmd = 'supervisorctl stop cozy-controller ; sleep 10'
        cmd += ' ; service couchdb stop ; service nginx stop'
        cmd += ' ; rm -rf /var/lib/couchdb/.cozy_design'
        cmd += ' /var/lib/couchdb/_replicator.couch'
        cmd += ' ; tar xvzf {} -C /'
        cmd += ' ; service couchdb start ; service nginx start'
        cmd = cmd.format(backup_file)
        helpers.cmd_exec(cmd, show_output=True)
        helpers.wait_couchdb(10)
        cmd = 'supervisorctl start cozy-controller'
        helpers.cmd_exec(cmd, show_output=True)
