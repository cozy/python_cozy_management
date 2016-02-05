'''
    Some migrations helpers
'''

from . import ssl
from . import helpers
from . import monitor

PREFIX = '/usr/local/cozy/apps'


def rebuild_app(app_name, quiet=False, force=True, without_exec=False):
    '''
        Rebuild cozy apps with deletion of npm directory & new npm build
    '''
    user = 'cozy-{app_name}'.format(app_name=app_name)
    home = '{prefix}/{app_name}'.format(prefix=PREFIX, app_name=app_name)
    command_line = 'cd {home}'.format(home=home)
    if force:
        command_line += ' && rm -rf node_modules'
    command_line += ' && chown -R {user}:{user} .'.format(user=user)
    command_line += ' && sudo -u {user} env HOME={home} npm install'.format(
        user=user,
        home=home
    )

    if not quiet:
        print 'Execute:'
        print command_line

    if not without_exec:
        result = helpers.cmd_exec(command_line)
        print result['stdout']
        print result['stderr']
        print result['error']


def rebuild_all_apps():
    '''
        Get all cozy apps & rebuild npm repository
    '''
    cozy_apps = monitor.status(only_cozy=True)
    for app in cozy_apps.keys():
        rebuild_app(app, force=True)


def restart_stopped_apps():
    '''
        Restart all apps in stopped state
    '''
    cozy_apps = monitor.status(only_cozy=True)
    for app in cozy_apps.keys():
        state = cozy_apps[app]
        if state == 'up':
            next
        elif state == 'down':
            print 'Start {}'.format(app)
            rebuild_app(app, force=False)
            monitor.start(app)


def migrate_2_node4():
    '''
        Migrate existing cozy to node4
    '''
    helpers.cmd_exec('update-cozy-stack', show_output=True)
    helpers.cmd_exec('update-all', show_output=True)
    ssl.normalize_cert_dir()
    helpers.cmd_exec('apt-get update', show_output=True)
    helpers.cmd_exec('apt-get install -y cozy-apt-node-list', show_output=True)
    helpers.cmd_exec('apt-get update', show_output=True)
    helpers.cmd_exec('apt-get install -y cozy', show_output=True)
    helpers.cmd_exec('npm install -g cozy-monitor cozy-controller',
                     show_output=True)
    rebuild_all_apps()
    helpers.cmd_exec('supervisorctl restart cozy-controller', show_output=True)
    restart_stopped_apps()
