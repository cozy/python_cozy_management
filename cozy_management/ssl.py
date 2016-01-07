'''
    SSL Certificate management
'''

import os
import OpenSSL.crypto

CERTIFICATES_PATH = '/etc/cozy/certs'
OLD_CERTIFICATE_PATH = '/etc/cozy/server.crt'
OLD_PRIVATE_KEY_PATH = '/etc/cozy/server.key'
CURRENT_CERTIFICATE_PATH = OLD_CERTIFICATE_PATH
CURRENT_PRIVATE_KEY_PATH = OLD_PRIVATE_KEY_PATH


def get_crt_common_name(certificate_path=OLD_CERTIFICATE_PATH):
    '''
        Get CN from certificate
    '''
    certificate_file = open(certificate_path)
    crt = OpenSSL.crypto.load_certificate(OpenSSL.crypto.FILETYPE_PEM,
                                          certificate_file.read())
    return crt.get_subject().commonName


def move_old_path_to_new_standard():
    '''
        Put old cerfificate form to new one
    '''
    current_cn = get_crt_common_name()

    if not os.path.isdir(CERTIFICATES_PATH):
        print 'Need to create {}'.format(CERTIFICATES_PATH)
        os.mkdir(CERTIFICATES_PATH, 0755)

    if os.path.isfile(OLD_CERTIFICATE_PATH) and \
            not os.path.islink(OLD_CERTIFICATE_PATH):
        target = '{}/{}.crt'.format(CERTIFICATES_PATH, current_cn)
        print 'Move {} to {}'.format(CERTIFICATES_PATH, target)
        os.rename(OLD_CERTIFICATE_PATH, target)
        print 'Create symlink {} -> {}'.format(CURRENT_CERTIFICATE_PATH,
                                               target)
        os.symlink(target, CURRENT_CERTIFICATE_PATH)
    else:
        print 'Nothing to do for {}'.format(OLD_CERTIFICATE_PATH)

    if os.path.isfile(OLD_PRIVATE_KEY_PATH) and \
            not os.path.islink(OLD_PRIVATE_KEY_PATH):
        target = '{}/{}.key'.format(CERTIFICATES_PATH, current_cn)
        print 'Move {} to {}'.format(OLD_PRIVATE_KEY_PATH, target)
        os.rename(OLD_PRIVATE_KEY_PATH, target)
        print 'Create symlink {} -> {}'.format(CURRENT_PRIVATE_KEY_PATH,
                                               target)
        os.symlink(target, CURRENT_PRIVATE_KEY_PATH)
    else:
        print 'Nothing to do for {}'.format(OLD_PRIVATE_KEY_PATH)
