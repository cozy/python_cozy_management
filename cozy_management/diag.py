'''
    Diag helper
'''
import re
import glob
import json
import platform

import couchdb
import helpers

HOSTNAMES = [platform.node()]
IP_ADDRESSES = helpers.get_ip_addresses()


def _clean_result(string_to_clean):
    string_cleaned = string_to_clean
    string_cleaned = re.sub(r'{}'.format('|'.join(HOSTNAMES)), 'the-hostname', string_cleaned)
    string_cleaned = re.sub(r'{}'.format('|'.join(IP_ADDRESSES)), '127.3.2.1', string_cleaned)

    return string_cleaned


def exec_and_print(command_line, text=None):
    if text is None:
        text = command_line
    result = helpers.cmd_exec(command_line)
    print '===== {}'.format(text)
    print _clean_result(helpers.array_2_str(result['stderr']))
    print _clean_result(helpers.array_2_str(result['stdout']))


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
        print helpers.array_2_str(helpers.cmd_exec('ls -l {}'.format(db_directory))['stdout'])


def _show_couchdb_result(url='/'):
    print '===== show couchdb /'
    print(json.dumps(
        couchdb.curl_couchdb(url).json(),
        sort_keys=True,
        indent=2
        ))

def show():
    from pprint import pprint

    exec_and_print('lsb_release -a')
    exec_and_print('uname -a')
    exec_and_print('which node nodejs', 'nodejs path')
    exec_and_print('node -v ; nodejs -v', 'node & nodejs version')
    exec_and_print('npm -g ls -depth 0', 'npm packages')
    exec_and_print('pip list')
    exec_and_print('supervisorctl status')
    _show_files_content('/etc/supervisor/conf.d/cozy-*.conf')
    exec_and_print('which systemctl && systemctl status couchdb.service', 'systemctl status couchdb.service')
    _show_couchdb_database_dir()
    _show_couchdb_database_dir_content()
    print '===== ping couchdb'
    couchdb_ping = couchdb.ping()
    print couchdb_ping
    if couchdb_ping:
        _show_couchdb_result()
        _show_couchdb_result('/cozy')
    exec_and_print('ls -l /etc/cozy')
    exec_and_print('find /usr/local/cozy* -type d -maxdepth 2 -ls', 'find /usr/local/cozy*')
    exec_and_print('for f in /var/log/supervisor/cozy-*stdout*.log /usr/local/var/log/cozy/*; do echo "=== $f" ; tail -20 $f; echo; done', 'All logs')


if __name__ == '__main__':
    show()
