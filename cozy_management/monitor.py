'''
A cozy-monitor parser
'''

import re
import inspect
import subprocess


# Regexp to remove color in output
ANSI_ESCAPE = re.compile(r'\x1b[^m]*m')
SYSTEM_APPS = ['controller', 'couch', 'mta']


def launch_command(command, parameter=''):
    '''Can launch a cozy-monitor command

    :param command: The cozy-monitor command to launch
    :param parameter: The parameter to push on cozy-monitor if needed
    :returns: the command string
    '''
    result = ''

    # Transform into an array if it not one
    if not isinstance(parameter, list):
        parameter = [parameter]

    # Iterate on all parameter with action & put them in result string
    for name in parameter:
        result += subprocess.Popen('cozy-monitor {} {}'.format(command, name),
                                   shell=True,
                                   stdout=subprocess.PIPE).stdout.read()
    return result


def status(app_name=None, only_cozy=False, as_boolean=False):
    '''Get apps status

    :param app_name: If pass app name return this app status
    :return: dict with all apps status or str with one app status
    '''
    apps = {}
    # Get all apps status & slip them
    apps_status = subprocess.Popen('cozy-monitor status',
                                   shell=True,
                                   stdout=subprocess.PIPE).stdout.read()
    apps_status = apps_status.split('\n')

    # Parse result to store them in apps dictionary
    for app_status in apps_status:
        if app_status:
            app_status = ANSI_ESCAPE.sub('', app_status).split(': ')
            if len(app_status) == 2:
                current_status = app_status[1]
                if as_boolean:
                    if app_status[1] == 'up':
                        current_status = True
                    else:
                        current_status = False
                if only_cozy and app_status[0] not in SYSTEM_APPS:
                    apps[app_status[0]] = current_status
                else:
                    apps[app_status[0]] = current_status

    # Return app status if get as param or return all apps status
    if app_name:
        return apps.get(app_name, None)
    else:
        return apps


def views_list():
    '''Get views list

    :returns: Formated string
    '''
    return launch_command('views-list')


def compact_all_views():
    '''Compact all views

    :returns: Formated string
    '''
    return launch_command('compact-all-views')


def compact_views(view):
    '''Compact one views

    :param view: The view to compact
    :returns: Formated string
    '''
    return launch_command('compact-views', view)


# inspect.stack()[0][3] -> return the current method name
def compact():
    '''Launch Cozy CouchDB compact

    :returns: Formated string
    '''
    return launch_command(inspect.stack()[0][3])


def stop(app_name):
    '''Stop app name or app list

    :param app_name: An app name or an apps list
    :returns: Formated string
    '''
    return launch_command(inspect.stack()[0][3], app_name)


def start(app_name):
    '''Start app name or app list

    :param app_name: An app name or an apps list
    :returns: Formated string
    '''
    return launch_command(inspect.stack()[0][3], app_name)


def restart(app_name):
    '''Restart app name or app list

    :param app_name: An app name or an apps list
    :returns: Formated string
    '''
    return launch_command(inspect.stack()[0][3], app_name)


def update(app_name):
    '''Update app name or app list

    :param app_name: An app name or an apps list
    :returns: Formated string
    '''
    return launch_command(inspect.stack()[0][3], app_name)


def uninstall(app_name):
    '''Uninstall app name or app list

    :param app_name: An app name or an apps list
    :returns: Formated string
    '''
    return launch_command(inspect.stack()[0][3], app_name)


def install(app_name):
    '''Install app name or app list

    :param app_name: An app name or an apps list
    :returns: Formated string
    '''
    return launch_command(inspect.stack()[0][3], app_name)
