'''
    Some migrations helpers
'''

from . import helpers
from . import monitor

PREFIX='/usr/local/cozy/apps'


def rebuild_app(app_name, quiet=False, force=True, without_exec=False):
    '''
        Rebuild cozy apps with deletion of npm directory & new npm build
    '''
    user='cozy-{app_name}'.format(app_name=app_name)
    home='{prefix}/{app_name}'.format(prefix=PREFIX, app_name=app_name)
    command_line = 'cd {home}'.format(home=home)
    if force:
        command_line += ' && rm -rf node_modules'
    command_line += ' && chown -R {user}:{user} .'.format(user=user)
    command_line += '&& sudo -u {user} env HOME={home} npm install'.format(
            user=user,
            home=home
            )

    if not quiet:
        print 'Execute:'
        print command_line

    if not without_exec:
        print 'Go:'
        result = helpers.cmd_exec(command_line)
        print result['stdout']
        print result['stderr']
        print result['error']


def update_all_apps():
    '''
        Get all cozy apps & rebuild npm repository
    '''
    from pprint import pprint
    cozy_apps = monitor.status(only_cozy=True)
    for app in cozy_apps.keys():
        rebuild_app(app, force=True)
