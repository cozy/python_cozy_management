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

FILETYPE_PEM = OpenSSL.crypto.FILETYPE_PEM
TYPE_RSA = OpenSSL.crypto.TYPE_RSA


def generate_key(common_name, size=4096, digest='sha256'):
    '''
        Generate private key and certificate for https
    '''
    private_key = OpenSSL.crypto.PKey()
    private_key.generate_key(TYPE_RSA, size)

    request = OpenSSL.crypto.X509Req()
    subject = request.get_subject()
    setattr(subject, 'CN', common_name)
    request.set_pubkey(private_key)
    request.sign(private_key, digest)

    certificate = OpenSSL.crypto.X509()
    certificate.set_serial_number(0)
    certificate.gmtime_adj_notBefore(0)
    certificate.gmtime_adj_notAfter(60*60*24*365*5)
    certificate.set_issuer(request.get_subject())
    certificate.set_subject(request.get_subject())
    certificate.set_pubkey(request.get_pubkey())
    certificate.sign(private_key, digest)

    private_key_path = '{}/{}.key'.format(CERTIFICATES_PATH, common_name)
    if not os.path.isfile(private_key_path):
        print 'Write {}'.format(private_key_path)
        with open(private_key_path, 'w+') as private_key_file:
            private_key_file.write(
                OpenSSL.crypto.dump_privatekey(FILETYPE_PEM,
                                               private_key).decode('utf-8')
            )
    else:
        print 'Already exist: {}'.format(private_key_path)

    certificate_path = '{}/{}.crt'.format(CERTIFICATES_PATH, common_name)
    if not os.path.isfile(certificate_path):
        print 'Write {}'.format(certificate_path)
        with open(certificate_path, 'w+') as certificate_file:
            certificate_file.write(
                OpenSSL.crypto.dump_certificate(FILETYPE_PEM,
                                                certificate).decode('utf-8')
            )
    else:
        print 'Already exist: {}'.format(certificate_path)

    clean_links()
    make_links(common_name)


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
    else:
        print 'Nothing to do for {}'.format(OLD_CERTIFICATE_PATH)

    if os.path.isfile(OLD_PRIVATE_KEY_PATH) and \
            not os.path.islink(OLD_PRIVATE_KEY_PATH):
        target = '{}/{}.key'.format(CERTIFICATES_PATH, current_cn)
        print 'Move {} to {}'.format(OLD_PRIVATE_KEY_PATH, target)
        os.rename(OLD_PRIVATE_KEY_PATH, target)
    else:
        print 'Nothing to do for {}'.format(OLD_PRIVATE_KEY_PATH)

    make_links(current_cn)


def clean_links():
    '''
        Clean symlink for nginx
    '''
    if os.path.isfile(CURRENT_CERTIFICATE_PATH):
        print 'Delete symlink {}'.format(CURRENT_CERTIFICATE_PATH)
        os.remove(CURRENT_CERTIFICATE_PATH)

    if os.path.isfile(CURRENT_PRIVATE_KEY_PATH):
        print 'Delete symlink {}'.format(CURRENT_PRIVATE_KEY_PATH)
        os.remove(CURRENT_PRIVATE_KEY_PATH)


def make_links(current_cn):
    '''
        Create symlink for nginx
    '''
    if not os.path.isfile(CURRENT_CERTIFICATE_PATH):
        target = '{}/{}.crt'.format(CERTIFICATES_PATH, current_cn)
        print 'Create symlink {} -> {}'.format(CURRENT_CERTIFICATE_PATH,
                                               target)
        os.symlink(target, CURRENT_CERTIFICATE_PATH)

    if not os.path.isfile(CURRENT_PRIVATE_KEY_PATH):
        target = '{}/{}.key'.format(CERTIFICATES_PATH, current_cn)
        print 'Create symlink {} -> {}'.format(CURRENT_PRIVATE_KEY_PATH,
                                               target)
        os.symlink(target, CURRENT_PRIVATE_KEY_PATH)
