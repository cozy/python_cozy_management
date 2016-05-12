'''Cozy management command line

Usage:
    cozy_management show_diag
    cozy_management show_reporting
    cozy_management ping_couchdb
    cozy_management get_admin
    cozy_management get_couchdb_admins
    cozy_management delete_token
    cozy_management create_token
    cozy_management create_cozy_db [--name <name>]
    cozy_management reset_token
    cozy_management get_cozy_param <name>
    cozy_management normalize_cert_dir
    cozy_management get_crt_common_name [<filename>]
    cozy_management clean_links
    cozy_management make_links <common_name>
    cozy_management generate_certificate <common_name> [--size <size>] [--digest <digest>]
    cozy_management sign_certificate <common_name>
    cozy_management regenerate_dhparam [--size <size>]
    cozy_management compare_version <current> <operator> <reference>
    cozy_management is_cozy_registered
    cozy_management unregister_cozy
    cozy_management fix_oom_scores
    cozy_management get_oom_scores
    cozy_management rebuild_app <app> [--not-force] [--restart]
    cozy_management rebuild_all_apps [--not-force] [--restart]
    cozy_management migrate_2_node4
    cozy_management install_requirements
    cozy_management install_cozy
    cozy_management wait_couchdb
    cozy_management wait_cozy_stack
    cozy_management check_lsb_codename
    cozy_management emulate_smtp [--bind <ip>] [--port <port>]
    cozy_management backup
    cozy_management restore <backup_filename>

Options:
    cozy_management -h | --help

'''

import sys
import smtpd
import docopt
import asyncore
from cozy_management import ssl
from cozy_management import backup
from cozy_management import couchdb
from cozy_management import diag
from cozy_management import process
from cozy_management import compare_version
from cozy_management import migration
from cozy_management import helpers


def main():
    '''
        Main part of command line utility
    '''
    arguments = docopt.docopt(__doc__, version='Naval Fate 2.0')

    if arguments['show_diag']:
        diag.show()

    if arguments['show_reporting']:
        diag.reporting()
        diag.show()

    if arguments['ping_couchdb']:
        try:
            if couchdb.ping():
                print 'OK'
            else:
                print 'KO'
        except:
            print 'KO'

    if arguments['get_admin']:
        (username, password) = couchdb.get_admin()
        print 'Username: {}'.format(username)
        print 'Password: {}'.format(password)

    if arguments['get_couchdb_admins']:
        admins = couchdb.get_couchdb_admins()
        print 'CouchDB admins:'
        for admin in admins:
            print '- {}'.format(admin)

    if arguments['delete_token']:
        couchdb.delete_token()

    if arguments['create_token']:
        print couchdb.create_token()

    if arguments['create_cozy_db']:
        if arguments['--name']:
            db_name = arguments.get('<name>', 'cozy')
        else:
            db_name = 'cozy'
        couchdb.create_cozy_db(db_name)
        print '{} DB is ready'.format(db_name)

    if arguments['reset_token']:
        couchdb.reset_token()
        print 'New tokens:'
        print couchdb.get_admin()[0]

    if arguments['get_cozy_param']:
        print couchdb.get_cozy_param(arguments['<name>'])

    if arguments['normalize_cert_dir']:
        ssl.normalize_cert_dir()

    if arguments['get_crt_common_name']:
        filename = arguments['<filename>']
        if filename:
            print ssl.get_crt_common_name(filename)
        else:
            print ssl.get_crt_common_name()

    if arguments['clean_links']:
        ssl.clean_links()

    if arguments['make_links']:
        ssl.make_links(arguments['<common_name>'])

    if arguments['generate_certificate']:
        common_name = arguments['<common_name>']

        if arguments['--size']:
            key_size = int(arguments['<size>'])
        else:
            key_size = ssl.DEFAULT_KEY_SIZE

        if arguments['--digest']:
            digest = arguments['<digest>']
        else:
            digest = ssl.DEFAULT_DIGEST

        print 'Generate certificate for {} with {} key size and {} digest'.format(common_name, key_size, digest)
        ssl.generate_certificate(common_name,
                                 key_size,
                                 digest)

    if arguments['sign_certificate']:
        common_name = arguments['<common_name>']

        print "Sign certificate for {} with Let's Encrypt".format(common_name)
        ssl.acme_sign_certificate(common_name)

    if arguments['regenerate_dhparam']:
        if arguments['--size']:
            size = int(arguments['<size>'])
        else:
            size = ssl.DEFAULT_DHPARAM_SIZE

        print 'Regenerate dhparam with {} size'.format(size)
        ssl.regenerate_dhparam(size)

    if arguments['compare_version']:
        current = arguments['<current>']
        operator = arguments['<operator>']
        reference = arguments['<reference>']
        compare_version.compare(current, operator, reference)

    if arguments['is_cozy_registered']:
        print couchdb.is_cozy_registered()

    if arguments['unregister_cozy']:
        couchdb.unregister_cozy()

    if arguments['fix_oom_scores']:
        process.fix_oom_scores()

    if arguments['get_oom_scores']:
        process.get_oom_scores()

    if arguments['rebuild_app']:
        if arguments['--not-force']:
            force = False
        else:
            force = True
        if arguments['--restart']:
            restart = True
        else:
            restart = False
        migration.rebuild_app(arguments['<app>'], force=force, restart=restart)

    if arguments['rebuild_all_apps']:
        if arguments['--not-force']:
            force = False
        else:
            force = True
        if arguments['--restart']:
            restart = True
        else:
            restart = False
        migration.rebuild_all_apps(force=force, restart=restart)

    if arguments['migrate_2_node4']:
        migration.migrate_2_node4()

    if arguments['install_requirements']:
        migration.install_requirements()

    if arguments['install_cozy']:
        migration.install_cozy()

    if arguments['wait_couchdb']:
        helpers.wait_couchdb()

    if arguments['wait_cozy_stack']:
        helpers.wait_cozy_stack()

    if arguments['check_lsb_codename']:
        sys.exit(diag.check_lsb_codename())

    if arguments['emulate_smtp']:
        ip = '127.0.0.1'
        port = '25'
        if arguments['--bind']:
            ip = arguments['<ip>']
        if arguments['--port']:
            if arguments['<port>']:  # a bug in docopt?
                port = arguments['<port>']
            else:
                port = arguments['<ip>']

        print 'Emulate SMTP server on {}:{}'.format(ip, port)
        smtpd.DebuggingServer(tuple([ip, int(port)]), None)
        asyncore.loop()

    if arguments['backup']:
        backup.backup()

    if arguments['restore']:
        backup.restore(arguments['<backup_filename>'])


if __name__ == '__main__':
    main()
