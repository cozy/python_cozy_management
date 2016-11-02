'''
    SSL Certificate management
'''

import os
import subprocess
import OpenSSL.crypto
from glob import glob
from datetime import datetime, timedelta
from stat import S_IXUSR

from . import helpers

COZY_CONFIG_PATH = '/etc/cozy'
CERTIFICATES_PATH = '{}/certs'.format(COZY_CONFIG_PATH)
ACME_PRIVATE_PATH = '{}/acme'.format(COZY_CONFIG_PATH)
ACME_PRIVATE_KEY = '{}/account.key'.format(ACME_PRIVATE_PATH)
ACME_INTERMEDIATE_CERT = '{}/lets-encrypt-cross-signed.pem'.format(ACME_PRIVATE_PATH)
ACME_INTERMEDIATE_CERT_URL = 'https://letsencrypt.org/certs/lets-encrypt-x3-cross-signed.pem'
OLD_CERTIFICATE_PATH = '{}/server.crt'.format(COZY_CONFIG_PATH)
OLD_PRIVATE_KEY_PATH = '{}/server.key'.format(COZY_CONFIG_PATH)
CURRENT_CERTIFICATE_PATH = OLD_CERTIFICATE_PATH
CURRENT_PRIVATE_KEY_PATH = OLD_PRIVATE_KEY_PATH
DEFAULT_KEY_SIZE = 4096
DEFAULT_DIGEST = 'sha256'

FILETYPE_PEM = OpenSSL.crypto.FILETYPE_PEM
TYPE_RSA = OpenSSL.crypto.TYPE_RSA


def generate_certificate(common_name, size=DEFAULT_KEY_SIZE):
    '''
        Generate private key and certificate for https
    '''

    private_key_path = '{}/{}.key'.format(CERTIFICATES_PATH, common_name)
    certificate_path = '{}/{}.crt'.format(CERTIFICATES_PATH, common_name)
    if not os.path.isfile(certificate_path):
        print 'Create {}'.format(certificate_path)
        cmd = 'openssl req -x509 -nodes -newkey rsa:{size} -keyout {private_key_path} -out {certificate_path} -days 3650 -subj "/CN={common_name}"'.format(
            size=size, private_key_path=private_key_path,
            certificate_path=certificate_path, common_name=common_name)
        p = subprocess.Popen(cmd,
                             shell=True,
                             stdout=subprocess.PIPE,
                             close_fds=True)
        p.communicate()
        helpers.file_rights(private_key_path, mode=0400, uid=0, gid=0)
        helpers.file_rights(certificate_path, mode=0444, uid=0, gid=0)
    else:
        print 'Already exist: {}'.format(certificate_path)

    clean_links()
    make_links(common_name)


def acme_init():
    '''
        Init acme key
    '''
    acme_private_key = ACME_PRIVATE_KEY
    acme_intermediate_cert = ACME_INTERMEDIATE_CERT
    acme_intermediate_cert_url = ACME_INTERMEDIATE_CERT_URL

    if not os.path.isfile(acme_private_key):
        print 'Create {}'.format(acme_private_key)
        cmd = 'openssl genrsa 4096 > {acme_private_key}'.format(
            acme_private_key=acme_private_key)
        p = subprocess.Popen(cmd,
                             shell=True,
                             stdout=subprocess.PIPE,
                             close_fds=True)
        p.communicate()
        helpers.file_rights(acme_private_key, mode=0444, uid=0, gid=0)
    else:
        print 'Already exist: {}'.format(acme_private_key)

    if not os.path.isfile(acme_intermediate_cert):
        print 'Create {}'.format(acme_intermediate_cert)
        cmd = 'wget -O - {acme_intermediate_cert_url} > {acme_intermediate_cert}'
        cmd = cmd.format(acme_intermediate_cert_url=acme_intermediate_cert_url,
                         acme_intermediate_cert=acme_intermediate_cert)
        p = subprocess.Popen(cmd,
                             shell=True,
                             stdout=subprocess.PIPE,
                             close_fds=True)
        p.communicate()
        helpers.file_rights(acme_intermediate_cert, mode=0444, uid=0, gid=0)
    else:
        print 'Already exist: {}'.format(acme_intermediate_cert)


def _internal_sign_certificate(certificate_path, certificate_request_path,
                              signed_cert):
    acme_init()
    cmd = 'acme_tiny.py --account-key {acme_private_key}'
    cmd += ' --csr {certificate_request_path}'
    cmd += ' --acme-dir /var/www/cozy-letsencrypt'
    cmd += ' > {signed_cert}'
    cmd = cmd.format(acme_private_key=ACME_PRIVATE_KEY,
                     certificate_request_path=certificate_request_path,
                     signed_cert=signed_cert)
    p = subprocess.Popen(cmd,
                         shell=True,
                         stdout=subprocess.PIPE,
                         close_fds=True)
    p.communicate()
    cmd = 'cat {signed_cert} {acme_intermediate_cert} > {certificate_path}'
    cmd = cmd.format(
        signed_cert=signed_cert,
        acme_intermediate_cert=ACME_INTERMEDIATE_CERT,
        certificate_path=certificate_path)
    p = subprocess.Popen(cmd,
                         shell=True,
                         stdout=subprocess.PIPE,
                         close_fds=True)
    p.communicate()


def acme_sign_certificate(common_name, size=DEFAULT_KEY_SIZE):
    '''
        Sign certificate with acme_tiny for let's encrypt
    '''
    private_key_path = '{}/{}.key'.format(CERTIFICATES_PATH, common_name)
    certificate_path = '{}/{}.crt'.format(CERTIFICATES_PATH, common_name)
    certificate_request_path = '{}/{}.csr'.format(CERTIFICATES_PATH,
                                                  common_name)
    signed_cert = '{certificates_path}/{common_name}-signed.crt'.format(
        certificates_path=CERTIFICATES_PATH,
        common_name=common_name)

    generate_certificate(common_name, size)

    cmd = 'openssl req -new -sha256 -key {private_key_path}'
    cmd += ' -subj "/CN={common_name}" -out {certificate_request_path}'
    cmd = cmd.format(
        private_key_path=private_key_path,
        common_name=common_name,
        certificate_request_path=certificate_request_path
    )
    p = subprocess.Popen(cmd,
                         shell=True,
                         stdout=subprocess.PIPE,
                         close_fds=True)
    p.communicate()

    _internal_sign_certificate(certificate_path, certificate_request_path,
                              signed_cert)

    cron = "/etc/cron.monthly/acme-renew"
    if not os.path.exists(cron):
        with open(cron, "w") as file:
            file.write("#!/bin/bash\ncozy_management renew_certificates\n")
        st = os.stat(cron)
        os.chmod(cron, st.st_mode | S_IXUSR)

def _parse_asn1_generalized_date(date):
    return datetime.strptime(date, "%Y%m%d%H%M%SZ")

def acme_renew_certificates():
    '''
        Renew certificates with acme_tiny for let's encrypt
    '''

    for csr in glob(os.path.join(CERTIFICATES_PATH, '*.csr')):
        common_name = os.path.basename(csr)
        common_name = os.path.splitext(common_name)[0]

        certificate_path = "{}.crt".format(common_name)
        certificate_path = os.path.join(CERTIFICATES_PATH, certificate_path)

        with open(certificate_path) as file:
            crt = OpenSSL.crypto.load_certificate(OpenSSL.crypto.FILETYPE_PEM,
                                                    file.read())
            expiration = crt.get_notAfter()
            expiration = _parse_asn1_generalized_date(expiration)
            remaining = expiration - datetime.utcnow()
            if remaining > timedelta(days=30):
                print "No need to renew {} ({})".format(certificate_path, remaining)
                continue
            print "Renewing {} ({})".format(certificate_path, remaining)

        certificate_request_path = "{}.csr".format(common_name)
        certificate_request_path = os.path.join(CERTIFICATES_PATH,
                                                certificate_request_path)

        signed_cert = "{}-signed.crt".format(common_name)
        signed_cert = os.path.join(CERTIFICATES_PATH,
                                    signed_cert)

        _internal_sign_certificate(certificate_path, certificate_request_path,
                                    signed_cert)


def generate_certificate_pure_python(common_name, size=DEFAULT_KEY_SIZE,
                                        digest=DEFAULT_DIGEST):
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
    certificate.gmtime_adj_notAfter(60 * 60 * 24 * 365 * 5)
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
        helpers.file_rights(private_key_path, mode=0400, uid=0, gid=0)
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
        helpers.file_rights(certificate_path, mode=0444, uid=0, gid=0)
    else:
        print 'Already exist: {}'.format(certificate_path)

    clean_links()
    make_links(common_name)


def get_crt_common_name(certificate_path=OLD_CERTIFICATE_PATH):
    '''
        Get CN from certificate
    '''
    try:
        certificate_file = open(certificate_path)
        crt = OpenSSL.crypto.load_certificate(OpenSSL.crypto.FILETYPE_PEM,
                                              certificate_file.read())
        return crt.get_subject().commonName
    except IOError:
        return None


def normalize_cert_dir():
    '''
        Put old cerfificate form to new one
    '''
    current_cn = get_crt_common_name()

    if not os.path.isdir(COZY_CONFIG_PATH):
        print 'Need to create {}'.format(COZY_CONFIG_PATH)
        os.mkdir(COZY_CONFIG_PATH, 0755)

    if not os.path.isdir(CERTIFICATES_PATH):
        print 'Need to create {}'.format(CERTIFICATES_PATH)
        os.mkdir(CERTIFICATES_PATH, 0755)

    if not os.path.isdir(ACME_PRIVATE_PATH):
        print 'Need to create {}'.format(ACME_PRIVATE_PATH)
        os.mkdir(ACME_PRIVATE_PATH, 0700)

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

    if current_cn:
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
