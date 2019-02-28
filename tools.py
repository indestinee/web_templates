from config import db
import time
import numpy as np
import multiprocessing
import psutil
import os

ps_lock = multiprocessing.Lock()

def add_log(content, user_id=-1):
    db.add_row('log', data={'content': content, 'user_id': user_id,\
            'time': time.time()})

bytes_suffix = ['B', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB']
def bytes_trans(x, cnt=0):
    while x >= 1024:
        x = x / 1024
        cnt += 1
    return '%.2f%s'%(x, bytes_suffix[cnt])

def query_ps(pid):
    x = psutil.Process(pid)
    data = {'username': x.username(), 'memory': bytes_trans(x.memory_info().rss),}
            # 'cpu': x.cpu_percent(interval=0.1), 'cpu_num': x.cpu_num()}
    return data

def query_cuda_usg():
    cmd = 'nvidia-smi pmon -c 1 -s m'
    ps = []
    process = os.popen(cmd)
    output = process.read()
    for row in output.split('\n'):
        row = row.strip().split(' ')
        x = [xx for xx in row if xx != '']
        try:
            int(x[0])
            ps.append(x)
        except: pass
    res = []
    for p in ps:
        pid = int(p[1])
        data = query_ps(pid)
        data['gpu_id'] = int(p[0])
        data['gpu_memory'] = bytes_trans(int(p[3]), 2)
        data['pid'] = pid
        res.append(data)
    return res

def disk():# {{{
    disks = psutil.disk_partitions()
    data = []
    for disk in disks:
        status = psutil.disk_usage(disk.mountpoint)
        data.append({
            'device': disk.device,
            'mountpoint': disk.mountpoint,
            'total': bytes_trans(status.total),
            'used': bytes_trans(status.used),
            'free': bytes_trans(status.free),
            'percent': status.percent,
        })
    return data
# }}}
def gpu():# {{{
    try: import GPUtil
    except Exception as e: return '{}'.format(e), []
    gpus = GPUtil.getGPUs()
    data = []
    for gpu in gpus:
        data.append({
            'total': bytes_trans(gpu.memoryTotal, 2),
            'free': bytes_trans(gpu.memoryFree, 2),
            'used': bytes_trans(gpu.memoryUsed, 2),
            'name': gpu.name,
            'load': round(gpu.load * 1000) / 10,
            'percent': round(gpu.memoryUtil * 1000)/10,
            'temperature': gpu.temperature,
        })
    if len(data) == 0: return 'No GPUs found.', data
    return '', data
# }}}
def _get_ps():# {{{
    memory = psutil.virtual_memory()
    swap = psutil.swap_memory()
    net = psutil.net_io_counters()
    disks = disk()
    msg, gpus = gpu()
    cpus = psutil.cpu_percent(percpu=True, interval=0.5)
    if msg == '':
        try: gpups = query_cuda_usg()
        except: gpups = []
    else:
        gpups = []
    data = {
        'gpu_msg': msg,
        'gpups': gpups,
        'gpu': gpus,
        'cpu': cpus,
        'cpu_mean': float(np.mean(cpus)),
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

global ps_list
ps_list = []
def get_ps():
    global ps_list
    t = time.time()

    q_cd = 1
    if len(ps_list) == 0 or t - ps_list[0] >= q_cd:
        with ps_lock:
            if len(ps_list) == 1 and t - ps_list[0] < q_cd:
                return ps_list[1]
            ps_list = [t, _get_ps()]

    return ps_list[1]
    
