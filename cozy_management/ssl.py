'''
    SSL Certificate management
'''

import os
import OpenSSL.crypto

CERTIFICATES_PATH = '/etc/cozy/certs'
OLD_CERTIFICATE_PATH = '/etc/cozy/server.crt'


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
    if not os.path.isdir(CERTIFICATES_PATH):
        print 'Need to create {}'.format(CERTIFICATES_PATH)
        os.mkdir(CERTIFICATES_PATH, 0755)
    if os.path.isfile(OLD_CERTIFICATE_PATH):
        current_cn = get_crt_common_name()
        target = '{}/{}.crt'.format(CERTIFICATES_PATH, current_cn)
        print 'move /etc/cozy/server.crt to {}'.format(target)
    else:
        print 'Nothing to do for /etc/cozy/server.crt'
