import argparse, os
from eic_utils.base import file_type
from tools import run


def get_args():
    """TODO: Docstring for get_arg.
    :returns: args
    """
    parser = argparse.ArgumentParser(description='description')
    parser.add_argument('--https', action='store_true', default=False)
    parser.add_argument('--public', action='store_true', default=False)
    parser.add_argument('--debug', action='store_true', default=False)
    parser.add_argument('--ftp', action='store_true', default=False)
    parser.add_argument('--ipv6', action='store_true', default=False)
    parser.add_argument('-p', '--port', type=int, default=7777)
    return parser.parse_args()

class WebConfig(object):
    def __init__(self):
        self.args = get_args()
        self.host = ('::' if self.args.ipv6 else '0.0.0.0')\
                if self.args.public else '127.0.0.1'

        self._static_folder = 'static'
        self._static_url_path = '/static'
        self._secret_key = os.urandom(16)
            
        self.app_params = {}

        if self.args.https:
            certificate = 'certificate'
            public_cert = os.path.join(certificate, 'server-cert.pem')
            private_cert = os.path.join(certificate, 'server-key.pem')
            if file_type(public_cert) != 'file' or file_type(private_cert) != 'file':
                if not os.path.isdir('certificate'):
                    os.makedirs('certificate')
                cmd = ';\n'.join([
                    'openssl genrsa -out ./certificate/server-key.pem 1024',
                    'openssl req -new -out ./certificate/server-req.csr'
                    ' -key certificate/server-key.pem',
                    'openssl x509 -req -in ./certificate/server-req.csr'
                    ' -out ./certificate/server-cert.pem -signkey'
                    ' ./certificate/server-key.pem -days 3650'
                ])
                os.system(cmd)
            self.app_params['ssl_context'] = (public_cert, private_cert)

web_cfg = WebConfig()
