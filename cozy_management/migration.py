'''
    Some migrations helpers
'''
import sys

from . import ssl
from . import helpers
from . import monitor

PREFIX = '/usr/local/cozy/apps'


def rebuild_app(app_name, quiet=False, force=True, without_exec=False,
                restart=False):
    '''
        Rebuild cozy apps with deletion of npm directory & new npm build
    '''
    user = 'cozy-{app_name}'.format(app_name=app_name)
    home = '{prefix}/{app_name}'.format(prefix=PREFIX, app_name=app_name)
    command_line = 'cd {home}'.format(home=home)
    command_line += ' && git pull'
    if force:
        command_line += ' && ([ -d node_modules ] && rm -rf node_modules || true)'
        command_line += ' && ([ -d .node-gyp ] && rm -rf .node-gyp || true)'
        command_line += ' && ([ -d .npm ] && rm -rf .npm || true)'
    command_line += ' && chown -R {user}:{user} .'.format(user=user)
    command_line += ' && sudo -u {user} env HOME={home} npm install'.format(
        user=user,
        home=home
    )
    if restart:
        command_line += ' && cozy-monitor update {app_name}'.format(
            app_name=app_name)
        command_line += ' && cozy-monitor restart {app_name}'.format(
            app_name=app_name)

    if not quiet:
        print 'Execute:'
        print command_line

    if not without_exec:
        result = helpers.cmd_exec(command_line)
        print result['stdout']
        print result['stderr']
        print result['error']


def rebuild_all_apps(force=True, restart=False):
    '''
        Get all cozy apps & rebuild npm repository
    '''
    cozy_apps = monitor.status(only_cozy=True)
    for app in cozy_apps.keys():
        rebuild_app(app, force=force, restart=restart)


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
    helpers.cmd_exec('npm install -g cozy-monitor cozy-controller',
                     show_output=True)
    rebuild_all_apps()
    helpers.cmd_exec('update-cozy-stack', show_output=True)
    helpers.cmd_exec('update-all', show_output=True)
    helpers.cmd_exec('rm /etc/supervisor/conf.d/cozy-indexer.conf',
                     show_output=True)
    helpers.cmd_exec('supervisorctl reload', show_output=True)
    helpers.wait_cozy_stack()
    ssl.normalize_cert_dir()
    helpers.cmd_exec('apt-get update', show_output=True)
    helpers.cmd_exec(
        'echo "cozy cozy/nodejs_apt_list text " | debconf-set-selections',
        show_output=True)
    helpers.cmd_exec('apt-get install -y cozy-apt-node-list', show_output=True)
    helpers.cmd_exec('apt-get update', show_output=True)
    helpers.cmd_exec('apt-get install -y nodejs', show_output=True)
    helpers.cmd_exec('apt-get install -y cozy', show_output=True)
    helpers.cmd_exec('npm install -g cozy-monitor cozy-controller',
                     show_output=True)
    rebuild_app('data-system')
    rebuild_app('home')
    rebuild_app('proxy')
    helpers.cmd_exec('supervisorctl restart cozy-controller', show_output=True)
    helpers.wait_cozy_stack()
    rebuild_all_apps(restart=True)
    restart_stopped_apps()
    helpers.cmd_exec('apt-get install -y cozy', show_output=True)


def install_requirements():
    '''
        Install cozy requirements
    '''
    helpers.cmd_exec(
        'echo "cozy cozy/nodejs_apt_list text " | debconf-set-selections',
        show_output=True)
    helpers.cmd_exec('apt-get install -y cozy-apt-node-list', show_output=True)
    helpers.cmd_exec('apt-get update', show_output=True)
    command_line = 'apt-get install -y nodejs'
    command_line += ' && apt-get install -y cozy-depends'
    return_code = helpers.cmd_exec(command_line, show_output=True)
    if return_code != 0:
        sys.exit(return_code)


def install_cozy():
    '''
        Install a cozy
    '''
    install_requirements()
    command_line = 'apt-get install -y cozy'
    helpers.cmd_exec(command_line, show_output=True)
