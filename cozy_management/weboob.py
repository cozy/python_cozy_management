#!/usr/bin/env python
'''
    Weboob management
'''

import os
import shutil

from helpers import cmd_exec

WEBOOB_REPO = 'git://git.symlink.me/pub/weboob/devel.git'


def get_weboob_version():
    result = cmd_exec('weboob-cli --version')
    if (not result['error']):
        return result['stdout'].rstrip()

    return None


def update():
    print 'Updating weboob configuration'
    result = cmd_exec('weboob-config update')
    if (result['error']):
        print result['stderr']
        print 'Update failed'
    else:
        print 'Update succeeded'


def install():
    '''
        Install weboob system-wide
    '''
    tmp_weboob_dir = '/tmp/weboob'

    # Check that the directory does not already exists
    while (os.path.exists(tmp_weboob_dir)):
        tmp_weboob_dir += '1'

    # Clone the repository
    print 'Fetching sources in temporary dir {}'.format(tmp_weboob_dir)
    result = cmd_exec('git clone {} {}'.format(WEBOOB_REPO, tmp_weboob_dir))
    if (result['error']):
        print result['stderr']
        print 'Weboob installation failed: could not clone repository'
        exit()

    print 'Sources fetched, will now process to installation'

    # Launch the installation
    result = cmd_exec('cd {} && ./setup.py install'.format(tmp_weboob_dir))

    # Remove the weboob directory
    shutil.rmtree(tmp_weboob_dir)

    if (result['error']):
        print result['stderr']
        print 'Weboob installation failed: setup failed'
        exit()

    print result['stdout']

    # Check weboob version
    weboob_version = get_weboob_version()
    if (not weboob_version):
        print 'Weboob installation failed: version not detected'
        exit()

    print 'Weboob (version: {}) installation succeeded'.format(weboob_version)
    update()
