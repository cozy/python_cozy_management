'''
    Diag helper
'''
import re
import sys
import glob
import json
import platform
import requests

import couchdb
import helpers

HOSTNAMES = [platform.node()]
IP_ADDRESSES = helpers.get_ip_addresses()

SUPPORT_GENERIC_MESSAGE = '''\

If you have any issue you can't solve with this tool. Prepare outpout of
`cozy_management show_reporting` in a https://framabin.org/ and contact us on:
https://forum.cozy.io/
or
IRC freenode #cozycloud
'''

COUCH_AUTH_KO_MSG = '''\

Cozy need a CouchDB working. Try to check /etc/cozy/couchdb.login with CouchDB
credentials.
'''

COUCH_KO_MSG = '''\

Cozy need a CouchDB working. Try:
    systemctl start couchdb
or
    service start couchdb
'''

CONTROLLER_KO_MSG = '''\

Cozy controller may not started. Try :
    supervisorctl start cozy-controller
or check start messages with:
    NODE_ENV=production cozy-controller
'''

RP_HTTPS_KO_MSG = '''\

If you haven't any reverse proxy made your SSL termination, your cozy may not
work.  Try to start nginx or apache if you have install it. Or install nginx if
not.
'''

RP_HTTP_KO_MSG = '''\

If you haven't any reverse proxy listen on http, the http to https redirection
may not work.  Try to start nginx or apache if you have install it. Or install
nginx if not.
'''


def _clean_result(string_to_clean):
    string_cleaned = string_to_clean
    string_cleaned = re.sub(r'{}'.format('|'.join(HOSTNAMES)),
                            'the-hostname', string_cleaned)
    string_cleaned = re.sub(r'{}'.format('|'.join(IP_ADDRESSES)),
                            '127.3.2.1', string_cleaned)

    return string_cleaned


def exec_and_print(command_line, text=None):
    if text is None:
        text = command_line
    result = helpers.cmd_exec(command_line)
    print '===== {}'.format(text)
    print _clean_result(result['stderr'])
    print _clean_result(result['stdout'])


def _show_files_content(file_pattern, text=None):
    if text is None:
        text = file_pattern
    print '===== {}'.format(text)
    for filename in glob.glob(file_pattern):
        print '=== {}'.format(filename)
        print _clean_result(''.join(open(filename).readlines()))


def _show_couchdb_database_dir():
    database_dir = couchdb.get_database_dir()
    print '===== couchdb database directory'
    for filename in database_dir:
        print '{}: {}'.format(filename, database_dir[filename])


def _show_couchdb_database_dir_content():
    database_dir = couchdb.get_database_dir()
    print '===== couchdb database list'
    for filename in database_dir:
        db_directory = database_dir[filename]
        print '=== {}'.format(db_directory)
        print helpers.cmd_exec('ls -l {}'.format(db_directory))['stdout']


def _show_couchdb_result(url='/'):
    print '===== show couchdb /'
    print(json.dumps(
        couchdb.curl_couchdb(url).json(),
        sort_keys=True,
        indent=2
        ))


def _curl(url):
    try:
        requests.packages.urllib3.disable_warnings()
    except AttributeError:
        pass
    try:
        req = requests.get('{}'.format(url), verify=False)
    except requests.exceptions.ConnectionError:
        return False

    if req.status_code == 200:
        return True
    else:
        return False


def _die(message):
    print message
    print SUPPORT_GENERIC_MESSAGE
    sys.exit(0)


def check_lsb_codename():
    codename = helpers.cmd_exec('lsb_release -cs')['stdout'].rstrip('\n')
    if codename not in ['jessie', 'trusty']:
        print '[KO] you need to install Cozy on Debian jessie or Ubuntu trusty'
        print '!!!! If you continue, we can\'t support your installation.'
        return -1
    else:
        return 0


def reporting():
    exec_and_print('lsb_release -a')
    check_lsb_codename()
    exec_and_print('uname -a')
    exec_and_print('which node nodejs', 'nodejs path')
    exec_and_print('node -v ; nodejs -v', 'node & nodejs version')
    exec_and_print('npm -g ls -depth 0', 'npm packages')
    exec_and_print('python -V')
    exec_and_print('pip list')
    exec_and_print('supervisorctl status')
    _show_files_content('/etc/supervisor/conf.d/cozy-*.conf')
    exec_and_print('which systemctl && systemctl status couchdb.service',
                   'systemctl status couchdb.service')
    _show_couchdb_database_dir()
    _show_couchdb_database_dir_content()
    print '===== ping couchdb'
    couchdb_ping = couchdb.ping()
    print couchdb_ping
    if couchdb_ping:
        _show_couchdb_result()
        _show_couchdb_result('/cozy')
    exec_and_print('ls -l /etc/cozy')
    exec_and_print('find /usr/local/cozy* -type d -maxdepth 2 -ls',
                   'find /usr/local/cozy*')
    find_and_tail_files_cmd = (
        'for f in /var/log/supervisor/cozy-*stdout*.log '
        '/usr/local/var/log/cozy/*; do '
        'echo "=== $f" ; tail -20 $f; echo; '
        'done')
    exec_and_print(find_and_tail_files_cmd, 'All logs')
    exec_and_print('cozy-monitor status')
    exec_and_print('cozy-monitor versions')


def show():
    check_lsb_codename()
    try:
        couchdb_ping = couchdb.ping()
    except couchdb.HTTPError:
        print '[KO] CouchDB'
        _die(COUCH_AUTH_KO_MSG)

    if couchdb_ping:
        print '[OK] CouchDB'
    else:
        print '[KO] CouchDB'
        couchdb_http_ping = _curl('http://127.0.0.1:5984')
        if not couchdb_http_ping:
            _die(COUCH_KO_MSG)

    controller_ping = _curl('http://127.0.0.1:9002')
    if controller_ping:
        print '[OK] Cozy Controller'
    else:
        print '[KO] Cozy Controller'
        exec_and_print('supervisorctl status')
        _die(CONTROLLER_KO_MSG)

    rp_ping = _curl('https://127.0.0.1')
    if rp_ping:
        print '[OK] Cozy Reverse Proxy (https)'
    else:
        print '[KO] Cozy Reverse Proxy (https)'
        print RP_HTTPS_KO_MSG

    rp_ping = _curl('http://127.0.0.1')
    if rp_ping:
        print '[OK] Cozy Reverse Proxy (http)'
    else:
        print '[KO] Cozy Reverse Proxy (http)'
        print RP_HTTP_KO_MSG
