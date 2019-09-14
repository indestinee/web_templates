import os, time, stat, time
from database import db
import threadpool, threading
from tools import run


file_labels = ['B', 'KB', 'MB', 'GB', 'TB']

format_time = lambda localtime: time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(localtime))

def download(url, path, t):
    data = {'url': url, 'path': path, 'type': t, 'time': time.time(), 'status': 0}
    res = db.select('download', keys='id', limitation={'url=': url, 'path=': path, 'type=': t})
    if len(res):
        return res[0]['id']

    limitation = {'url=': url, 'path=': path, 'type=': t}
    res = db.insert('download', data)
    res = db.select('download', keys='id', limitation=limitation)
    return res[0]['id']


def file_type(mode):
    if stat.S_ISREG(mode):
        return 'file'
    if stat.S_ISDIR(mode):
        return 'dir'
    if stat.S_ISLNK(mode):
        return 'link'
    return 'unknown'

def format_byte(size):
    cnt = 0
    while size >= 1024:
        size /= 1024
        cnt += 1
    return '{:.2f}{}'.format(size, file_labels[cnt])

def get_files(path):
    res = []
    filenames = ['.', '..'] + os.listdir(path)
    for filename in filenames:
        try:
            stat = os.stat(os.path.join(path, filename))
            data = {
                'name': filename,
                'size': format_byte(stat.st_size),
                'last_modify': format_time(stat.st_mtime),
                'type': file_type(stat.st_mode),
            }
        except Exception as e:
            print(e)
            data = {}
        default = {
            'name': filename,
            'size': '??',
            'last_modify': '??',
            'type': '??',
        }
        default.update(data)
        res.append(default)
    return res


def download_url(url, path, **kwargs):
    cmd = 'wget --no-check-certificate -P {} {}'.format(path, url)
    print(cmd)
    return run(cmd)


def download_video(url, path, **kwargs):
    cmd = 'youtube-dl -o "{}/%(title)s.%(ext)s" {}'.format(path, url)
    print(cmd)
    return run(cmd)


def download_audio(url, path, **kwargs):
    cmd = 'youtube-dl -o "{}/%(title)s.%(ext)s" {} -x'.format(path, url)
    print(cmd)
    return run(cmd)


lock = threading.Lock()


def download_one(expired_time=86400):
    while True:
        with lock:
            item = db.select('download', limitation={'status<': 100, 'time<': time.time()}, extra='limit 1')
            if len(item) == 1:
                item = item[0]
                db.update('download', {'time': time.time() + expired_time}, limitation={'id=': item['id']})
            else:
                item = None
        if item is not None:
            try:
                if item['type'] == 'url':
                    download_url(**item)
                elif item['type'] == 'audio':
                    download_audio(**item)
                elif item['type'] == 'video':
                    download_video(**item)
                with lock:
                    db.update('download', {'time': time.time(), 'status': 100}, limitation={'id=': item['id']})
            except Exception as e:
                print(e)
                with lock:
                    db.update('download', {'time': time.time(), 'status': 100}, limitation={'id=': item['id']})


        time.sleep(5)           
