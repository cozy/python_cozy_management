'''Cozy management command line

Usage:
    cozy_management ping_couchdb
    cozy_management get_admin
    cozy_management get_couchdb_admins
    cozy_management delete_token
    cozy_management create_token
    cozy_management reset_token
    cozy_management get_cozy_param <name>

Options:
    cozy_management -h | --help

'''

import docopt
import cozy_management.couchdb


def main():
    '''
        Main part of command line utility
    '''
    arguments = docopt.docopt(__doc__, version='Naval Fate 2.0')

    if arguments['ping_couchdb']:
        try:
            if cozy_management.couchdb.ping_couchdb():
                print 'OK'
            else:
                print 'KO'
        except:
            print 'KO'

    if arguments['get_admin']:
        (username, password) = cozy_management.couchdb.get_admin()
        print 'Username: {}'.format(username)
        print 'Password: {}'.format(password)

    if arguments['get_couchdb_admins']:
        admins = cozy_management.couchdb.get_couchdb_admins()
        print 'CouchDB admins:'
        for admin in admins:
            print '- {}'.format(admin)

    if arguments['delete_token']:
        cozy_management.couchdb.delete_token()

    if arguments['create_token']:
        print cozy_management.couchdb.create_token()

    if arguments['reset_token']:
        cozy_management.couchdb.reset_token()
        print 'New tokens:'
        print cozy_management.couchdb.get_admin()[0]

    if arguments['get_cozy_param']:
        print cozy_management.couchdb.get_cozy_param(arguments['<name>'])


if __name__ == '__main__':
    main()
