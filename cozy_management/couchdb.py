'''
    CouchDB management
'''
import os
import random
import string
import requests

from . import helpers

LOGIN_FILENAME = "/etc/cozy/couchdb.login"
BASE_URL = 'http://127.0.0.1:5984'


class HTTPError(Exception):
    '''
        HTTP error exception
    '''
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


def id_generator(size=32,
                 chars=string.ascii_uppercase +
                 string.digits +
                 string.ascii_lowercase):
    '''
        Generates a random id
    '''

    return ''.join(random.choice(chars) for x in range(size))


def create_token_file(username=id_generator(), password=id_generator()):
    '''
        Store the admins password for further retrieve
    '''

    cozy_ds_uid = helpers.get_uid('cozy-data-system')
    if not os.path.isfile(LOGIN_FILENAME):
        with open(LOGIN_FILENAME, 'w+') as token_file:
            token_file.write("{0}\n{1}".format(username, password))

    helpers.file_rights(LOGIN_FILENAME, mode=0400, uid=cozy_ds_uid, gid=0)


def get_admin():
    '''
        Return the actual admin from token file
    '''
    if os.path.isfile(LOGIN_FILENAME):
        with open(LOGIN_FILENAME, 'r') as token_file:
            old_login, old_password = token_file.read().splitlines()[:2]
            return old_login, old_password
    else:
        return None, None


def curl_couchdb(url, method='GET', base_url=BASE_URL, data=None):
    '''
        Launch a curl on CouchDB instance
    '''
    (username, password) = get_admin()
    if username is None:
        auth = None
    else:
        auth = (username, password)

    if method == 'PUT':
        req = requests.put('{}{}'.format(base_url, url), auth=auth, data=data)
    elif method == 'DELETE':
        req = requests.delete('{}{}'.format(base_url, url), auth=auth)
    else:
        req = requests.get('{}{}'.format(base_url, url), auth=auth)

    if req.status_code not in [200, 201]:
        raise HTTPError('{}: {}'.format(req.status_code, req.text))
    return req


def get_couchdb_admins():
    '''
        Return the actual CouchDB admins
    '''
    user_list = []
    req = curl_couchdb('/_config/admins/')

    for user in req.json().keys():
        user_list.append(user)

    return user_list


def create_couchdb_admin(username, password):
    '''
        Create a CouchDB user
    '''
    curl_couchdb('/_config/admins/{}'.format(username),
                 method='PUT',
                 data='"{}"'.format(password))


def create_cozy_db(db_name='cozy'):
    '''
        Create a CouchDB cozy DB
    '''
    curl_couchdb('/{}'.format(db_name),
                 method='PUT')


def is_cozy_registered():
    '''
        Check if a Cozy is registered
    '''
    req = curl_couchdb('/cozy/_design/user/_view/all')
    users = req.json()['rows']

    if len(users) > 0:
        return True
    else:
        return False


def unregister_cozy():
    '''
        Unregister a cozy
    '''
    req = curl_couchdb('/cozy/_design/user/_view/all')
    users = req.json()['rows']

    if len(users) > 0:
        user = users[0]['value']
        user_id = user['_id']
        user_rev = user['_rev']

        print 'Delete cozy user: {}'.format(user_id)
        req = curl_couchdb('/cozy/{}?rev={}'.format(user_id, user_rev),
                           method='DELETE')

        return req.json()
    else:
        print 'Cozy not registered'
        return None


def delete_couchdb_admin(username):
    '''
        Delete a CouchDB user
    '''
    req = curl_couchdb('/_config/admins/{}'.format(username),
                       method='DELETE')

    return req.json()


def delete_all_couchdb_admins():
    '''
        Delete all CouchDB users
    '''
    # Get current cozy token
    username = get_admin()[0]
    # Get CouchDB admin list
    admins = get_couchdb_admins()

    # Delete all admin user excluding current
    for admin in admins:
        if admin == username:
            print "Delete {} later...".format(admin)
        else:
            print "Delete {}".format(admin)
            delete_couchdb_admin(admin)

    # Delete current CouchDB admin
    admin = username
    print "Delete {}".format(admin)
    delete_couchdb_admin(admin)


def delete_token():
    '''
        Delete current token, file & CouchDB admin user
    '''
    username = get_admin()[0]
    admins = get_couchdb_admins()

    # Delete current admin if exist
    if username in admins:
        print 'I delete {} CouchDB user'.format(username)
        delete_couchdb_admin(username)

    # Delete token file if exist
    if os.path.isfile(LOGIN_FILENAME):
        print 'I delete {} token file'.format(LOGIN_FILENAME)
        os.remove(LOGIN_FILENAME)


def create_token():
    '''
        Create token file & create user
    '''
    username = id_generator()
    password = id_generator()
    create_couchdb_admin(username, password)
    create_token_file(username, password)

    return 'Token {} created'.format(username)


def reset_token():
    '''
        Delete and recreate token including CouchDB admin user
    '''
    delete_token()
    create_token()


def ping():
    '''
        Ping CozyDB with existing credentials
    '''
    try:
        curl_couchdb('/cozy/')
        ping = True
    except requests.exceptions.ConnectionError, error:
        print error
        ping = False
    return ping


def get_cozy_param(param):
    '''
        Get parameter in Cozy configuration
    '''
    try:
        req = curl_couchdb('/cozy/_design/cozyinstance/_view/all')
        rows = req.json()['rows']
        if len(rows) == 0:
            return None
        else:
            return rows[0].get('value', {}).get(param, None)
    except:
        return None


def get_database_dir():
    import ConfigParser
    result = {}
    file_list = helpers.cmd_exec('find /usr/local/etc/couchdb /etc/couchdb -type f -name "*.ini"')
    file_list = file_list['stdout'].rstrip('\n').split('\n')
    for filename in file_list:
        config = ConfigParser.ConfigParser()
        config.readfp(open(filename))
        try:
            path = config.get('couchdb', 'database_dir')
            result[filename] = path
        except:
            pass
    return result
