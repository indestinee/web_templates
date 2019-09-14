import time, os, threadpool, threading, pickle, base64
from subprocess import Popen, PIPE
import numpy as np

from eic_utils.base import get_cur_time
from database import db

expired_time = 86400

random_str = lambda n: base64.b64encode(os.urandom(n)).decode('utf-8')

def add_log(content, user_id=-1):
    db.insert('log', {'content': content, 'user_id': user_id, 'time': time.time()})


def run(cmd):# {{{
    p = Popen(cmd, stdout=PIPE, stderr=PIPE, shell=True)
    stdout, stderror = p.communicate()
    if stderror is not None and len(stderror) > 0:
        raise Exception(stderror.decode('utf-8'))
    return stdout.decode('utf-8')
# }}}

bytes_suffix = ['B', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB']

def bytes_trans(x, cnt=0):
    while x >= 1024:
        x = x / 1024
        cnt += 1
    return '{:.2f}{}'.format(x, bytes_suffix[cnt])

def check_path(path):
    paths = []
    for each in path.split('/'):
        if each == '..':
            paths = paths[:-1]
        if each[-1] == '' or each[-1] == '.':
            continue
        paths.append(each)

    if len(paths) == 0:
        paths = ['.']

    path = '/'.join(paths)
    return path

