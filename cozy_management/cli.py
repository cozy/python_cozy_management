'''Cozy management command line

Usage:
    cozy_management ping_couchdb
    cozy_management get_admin
    cozy_management get_couchdb_admins
    cozy_management delete_token
    cozy_management create_token
    cozy_management reset_token
    cozy_management get_cozy_param <name>
    cozy_management normalize_cert_dir
    cozy_management get_crt_common_name [<filename>]
    cozy_management clean_links
    cozy_management make_links <common_name>
    cozy_management generate_certificate <common_name> [--size <size>] [--digest <digest>]
    cozy_management regenerate_dhparam [--size <size>]
    cozy_management compare_version <current> <operator> <reference>
    cozy_management is_cozy_registered
    cozy_management unregister_cozy
    cozy_management fix_oom_score

Options:
    cozy_management -h | --help

'''

import docopt
from cozy_management import ssl
from cozy_management import couchdb
from cozy_management import process
from cozy_management import compare_version


def main():
    '''
        Main part of command line utility
    '''
    arguments = docopt.docopt(__doc__, version='Naval Fate 2.0')

    if arguments['ping_couchdb']:
        try:
            if couchdb.ping_couchdb():
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

    if arguments['fix_oom_score']:
        process.fix_oom_score()


if __name__ == '__main__':
    main()
