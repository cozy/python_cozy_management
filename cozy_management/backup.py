'''
    Backup
'''

import os
import time

from . import helpers
from . import couchdb

BACKUPS_PATH = '/var/lib/cozy/backups'


def _get_couchdb_path():
    '''
        Get CouchDB .couch path
    '''
    database_dir = couchdb.get_database_dir()

    # get the first value that should be the couchdb path
    return database_dir[list(database_dir)[0]]


def backup(backup_filename=None):
    '''
        Backup a Cozy
    '''
    timestamp = time.strftime("%Y-%m-%d-%H-%M-%S", time.gmtime())

    if not backup_filename:
        if not os.path.isdir(BACKUPS_PATH):
            print 'Need to create {}'.format(BACKUPS_PATH)
            os.makedirs(BACKUPS_PATH, 0700)
        backup_filename = '{backups_path}/cozy-{timestamp}.tgz'.format(
            backups_path=BACKUPS_PATH,
            timestamp=timestamp
        )
    elif os.path.exists(backup_filename):
        print 'Backup file already exists: {}'.format(backup_filename)
        return

    couchdb_path = _get_couchdb_path()

    cmd = 'tar cvzf {backup_filename}'
    cmd += ' --exclude stack.token'
    cmd += ' --exclude couchdb.login'
    cmd += ' --exclude self-hosting.json'
    cmd += ' /etc/cozy /usr/local/var/cozy {couchdb_path}/cozy.couch'
    cmd = cmd.format(backup_filename=backup_filename,
                     couchdb_path=couchdb_path)
    helpers.cmd_exec(cmd, show_output=True)
    print 'Backup file: {}'.format(backup_filename)


def restore(backup_file):
    '''
        Restore a Cozy
        backup_file: path to .tar.gz
    '''
    if not os.path.isfile(backup_file) and not os.path.islink(backup_file):
        print 'Missing backup file: {}'.format(backup_file)
    else:
        couchdb_path = _get_couchdb_path()

        print 'Restore Cozy:'
        cmd = 'supervisorctl stop cozy-controller ; sleep 10'
        cmd += ' ; service couchdb stop ; service nginx stop'
        cmd += ' ; rm -rf {couchdb_path}/.cozy_design'
        cmd += ' {couchdb_path}/_replicator.couch'
        cmd += ' ; tar xvzf {backup_file} -C /'
        cmd += ' ; service couchdb start ; service nginx start'
        cmd = cmd.format(backup_file=backup_file, couchdb_path=couchdb_path)
        helpers.cmd_exec(cmd, show_output=True)
        helpers.wait_couchdb(10)
        cmd = 'supervisorctl start cozy-controller'
        helpers.cmd_exec(cmd, show_output=True)
