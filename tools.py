from config import db
import time
import psutil

def add_log(content, user_id=-1):
    db.add_row('log', data={'content': content, 'user_id': user_id,\
            'time': time.time()})

bytes_suffix = ['B', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB']
def bytes_trans(x):
    cnt = 0
    while x >= 1024:
        x = x / 1024
        cnt += 1
    return '%.2f%s'%(x, bytes_suffix[cnt])


def disk():# {{{
    disks = psutil.disk_partitions()
    data = []
    for disk in disks:
        status = psutil.disk_usage(disk.mountpoint)
        data.append({
            'device': disk.device,
            'mountpoint': disk.mountpoint,
            'total': status.total,
            'used': status.used,
            'free': status.free,
            'percent': status.percent,
        })
    return data
# }}}
def gpu():# {{{
    return 'gpu'
# }}}
def get_ps():# {{{
    memory = psutil.virtual_memory()
    swap = psutil.swap_memory()
    net = psutil.net_io_counters()
    disks = disk()
    data = {
        'cpu': psutil.cpu_percent(percpu=True, interval=1),
        'memory': {
            'total': bytes_trans(memory.total),
            'used': bytes_trans(memory.used),
            'free': bytes_trans(memory.free),
            'percent': memory.percent,
        }, 
        'swap': {
            'total': bytes_trans(swap.total),
            'used': bytes_trans(swap.used),
            'free': bytes_trans(swap.free),
            'percent': swap.percent,
        },
        'disks': disks,
        'net': {
            'bytes_sent': net.bytes_sent,
            'bytes_recv': net.bytes_recv,
        }
    }
    return data
# }}}
