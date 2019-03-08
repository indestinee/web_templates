from config import db
import time, psutil, os, threadpool, threading, pickle
import numpy as np
from utils import procedure
from subprocess import Popen, PIPE
from IPython import embed

expired_time = 86400



def add_log(content, user_id=-1):
    db.add_row('log', data={'content': content, 'user_id': user_id, 'time': time.time()})

def run(cmd):# {{{
    p = Popen(cmd, stdout=PIPE, stderr=PIPE, shell=True)
    stdout, stderror = p.communicate()
    if stderror is not None: raise Exception(stderror.decode('utf-8'))
    return stdout.decode('utf-8')
# }}}

bytes_suffix = ['B', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB']
def bytes_trans(x, cnt=0):
    while x >= 1024:
        x = x / 1024
        cnt += 1
    return '%.2f%s'%(x, bytes_suffix[cnt])

def query_ps(pid):
    x = psutil.Process(int(pid))
    data = {'username': x.username(), 'memory': bytes_trans(x.memory_info().rss), \
            'cpu': x.cpu_percent(interval=0.2), 'name': ' '.join(x.cmdline())}
    return data


class DataCollection(object):
    def __init__(self):
        self.gpu_tables = {}
        self.first = None
        self.last = None
        self._result = None

    def __update(self, func):# {{{
        self._result.update(func())
    # }}}
    def get_data(self, thread_num=2):# {{{
        self.last = self._result
        if self.first:
            thread_num = 1
            self.first = False
        self._result = {'time': time.time()}
        funcs = [self.get_cpus, self.get_gpus, self.get_disks,\
                self.get_memory, self.get_swap, self.get_nets,\
                self.get_gpups]

        if thread_num > 1:
            pool = threadpool.ThreadPool(thread_num)
            reqs = threadpool.makeRequests(self.__update, funcs)
            [pool.putRequest(req) for req in reqs]
            pool.wait()
        else:
            for func in funcs:
                self._result.update(func())
        return self._result
    # }}}
    def get_disks(self):# {{{
        disks = psutil.disk_partitions()
        results = []
        for disk in disks:
            status = psutil.disk_usage(disk.mountpoint)
            results.append({
                'device': disk.device,
                'mountpoint': disk.mountpoint,
                'total': bytes_trans(status.total),
                'used': bytes_trans(status.used),
                'percent': status.percent,
            })
        return {'disks': results}
    # }}}
    def get_gpus(self): # {{{
        cmd = 'nvidia-smi \
                --query-gpu=uuid,utilization.gpu,memory.total,memory.used,name,temperature.gpu \
                --format=csv,noheader,nounits'
        try:
            rows = run(cmd)
        except Exception as e:
            return {'gpu_msg': '{}'.format(e), 'gpu': []}

        gpus = []
        for i, row in enumerate(rows.split('\n')):
            row = row.strip()
            if row == '': continue
            uuid, load, total, used, name, temperature = row.split(',')
            self.gpu_tables[uuid] = i
            load, total, used = list(map(float, [load, total, used]))
            gpus.append({
                'total': bytes_trans(total, 2),
                'used': bytes_trans(used, 2),
                'name': name,
                'load': round(load),
                'percent': round(used/total*100),
                'temperature': temperature,
            })
        return {'gpu': gpus}
    # }}}
    def get_cpus(self, interval=0.5):# {{{
        cpus = psutil.cpu_percent(percpu=True, interval=interval)
        avg = float(np.mean(cpus))
        return {'cpu': cpus, 'cpu_mean': avg}
    # }}}
    def get_memory(self):# {{{
        memory = psutil.virtual_memory()
        return {'memory': {'total': bytes_trans(memory.total), 'used': bytes_trans(memory.used),\
                'percent': memory.percent,}}
    # }}}
    def get_swap(self):# {{{
        swap = psutil.swap_memory()
        return {'swap': {'total': bytes_trans(swap.total), 'used': bytes_trans(swap.used),\
                'percent': swap.percent,}}
    # }}}
    def get_nets(self):# {{{
        net = psutil.net_io_counters()
        delta_sent = 0 if self.last is None else net.bytes_sent - self.last['net']['bytes_sent']
        delta_recv = 0 if self.last is None else net.bytes_recv - self.last['net']['bytes_recv']
        return {'net': {'bytes_sent': net.bytes_sent, 'bytes_recv': net.bytes_recv,\
                'sent_speed': delta_sent/1024, 'recv_speed': delta_recv/1024,\
                'sent_speed_t': bytes_trans(delta_sent), 'recv_speed_t': bytes_trans(delta_recv)}} 
    # }}}
    def get_gpups(self):# {{{
        cmd = 'nvidia-smi \
                --query-compute-apps=gpu_uuid,pid,used_memory \
                --format=csv,noheader,nounits'
        try:
            rows = run(cmd)
        except Exception as e:
            return {'gpups': [], 'gpups_msg': '{}'.format(e)}

        res = []
        for row in rows.split('\n'):
            row = row.strip()
            if row == '': continue
            uuid, pid, memory = row.split(',')
            data = query_ps(pid)
            data['gpu_id'] = self.gpu_tables[uuid]
            data['gpu_memory'] = bytes_trans(float(memory), 2)
            data['pid'] = pid
            res.append(data)
        return {'gpups': res}
    # }}}

data_collection = DataCollection()

def auto_update():
    while True:
        data = data_collection.get_data()
        db.del_row('dashboard', limitation='time<{}'.format(time.time() - expired_time))
        db.add_row('dashboard', data={'data': pickle.dumps(data), 'time': data['time']})
        time.sleep(0.5)

thread = threading.Thread(target=auto_update)
thread.start()

def get_ps(from_time=None):
    if from_time is None: data = db.select('dashboard', extra='ORDER BY id DESC LIMIT 1')
    else: data = db.select('dashboard', keys="data", limitation='time>{}'.format(from_time), extra='ORDER BY id ASC')
    for each in data:
        each['data'] = pickle.loads(each['data'])
    return data
