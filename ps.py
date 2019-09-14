import psutil, time, threadpool, threading, pickle
import numpy as np

from tools import bytes_trans, run
from database import db

def query_process(pid):
    process_information = psutil.Process(int(pid))
    data = {
        'username': process_information.username(),
        'memory': bytes_trans(process_information.memory_info().rss),
        'cpu': process_information.cpu_percent(interval=0.2),
        'name': ' '.join(process_information.cmdline())
    }
    return data

class DataCollection(object):
    def __init__(self):
        self.gpu_tables = {}
        self.first = None
        self.last = None
        self.result = None

    def update(self, func):  # {{{
        self.result.update(func())
    # }}}

    def get_data(self, thread_num=2):# {{{
        self.last = self.result
        if self.first:
            thread_num = 1
            self.first = False
        self.result = {'time': time.time()}
        funcs = [
            self.get_cpu, self.get_gpu, self.get_disk,
            self.get_memory, self.get_swap, self.get_network,
            self.get_gpups
        ]

        if thread_num > 1:
            pool = threadpool.ThreadPool(thread_num)
            reqs = threadpool.makeRequests(self.update, funcs)
            [pool.putRequest(req) for req in reqs]
            pool.wait()
        else:
            for func in funcs:
                self.result.update(func())
        return self.result
    # }}}


    def get_disk(self):# {{{
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

    def get_gpu(self): # {{{
        cmd = 'nvidia-smi --query-gpu=uuid,utilization.gpu'\
              ',memory.total,memory.used,name,temperature.gpu'\
              ' --format=csv,noheader,nounits'
        try:
            rows = run(cmd)
        except Exception as e:
            return {'gpu_msg': '{}'.format(e), 'gpu': []}

        gpus = []
        for i, row in enumerate(rows.split('\n')):
            row = row.strip()
            if row == '':
                continue
            uuid, load, total, used, name, temperature = row.split(',')
            self.gpu_tables[uuid] = i
            load, total, used = list(map(float, [load, total, used]))
            gpus.append({
                'total': bytes_trans(total, 2),
                'used': bytes_trans(used, 2),
                'name': name,
                'load': round(load),
                'percent': round(used / total * 100),
                'temperature': temperature,
            })
        return {'gpu': gpus}
    # }}}

    def get_cpu(self, interval=0.5):# {{{
        cpus = psutil.cpu_percent(percpu=True, interval=interval)
        avg = float(np.mean(cpus))
        return {'cpu': cpus, 'cpu_mean': avg}
    # }}}

    def get_memory(self):# {{{
        memory = psutil.virtual_memory()
        return {
            'memory': {
                'total': bytes_trans(memory.total),
                'used': bytes_trans(memory.used),
                'percent': memory.percent
            }
        }
    # }}}

    def get_swap(self):# {{{
        swap = psutil.swap_memory()
        return {
            'swap': {
                'total': bytes_trans(swap.total),
                'used': bytes_trans(swap.used),
                'percent': swap.percent
            }
        }
    # }}}

    def get_network(self):# {{{
        net = psutil.net_io_counters()
        if self.last is None:
            delta_recv = 0
            delta_sent = 0
        else:
            delta_sent = net.bytes_sent - self.last['net']['bytes_sent']
            delta_recv = net.bytes_recv - self.last['net']['bytes_recv']

        return {
            'net': {
                'bytes_sent': net.bytes_sent, 'bytes_recv': net.bytes_recv,
                'sent_speed': delta_sent / 1024, 'recv_speed': delta_recv / 1024,
                'sent_speed_t': bytes_trans(delta_sent),
                'recv_speed_t': bytes_trans(delta_recv)
            }
        } 
    # }}}

    def get_gpups(self):# {{{
        cmd = 'nvidia-smi --query-compute-apps=gpu_uuid,pid,used_memory '\
            '--format=csv,noheader,nounits'

        try:
            rows = run(cmd)
        except Exception as e:
            return {'gpups': [], 'gpups_msg': '{}'.format(e)}

        res = []
        for row in rows.split('\n'):
            row = row.strip()
            if row == '':
                continue
            uuid, pid, memory = row.split(',')
            data = query_process(pid)
            data['gpu_id'] = self.gpu_tables[uuid]
            data['gpu_memory'] = bytes_trans(float(memory), 2)
            data['pid'] = pid
            res.append(data)
        return {'gpups': res}
    # }}}

def auto_update(expired_time=86400):
    while True:
        data = data_collection.get_data()
        db.delete('dashboard', limitation={'time<': time.time() - expired_time})
        db.insert('dashboard', rows={
            'data': pickle.dumps(data), 'time': data['time']})
        time.sleep(1)

def get_runtime_rss(from_time=None):
    if from_time is None:
        data = db.select('dashboard', extra='ORDER BY id DESC LIMIT 1')
    else:
        data = db.select('dashboard', keys="data",
                         limitation={'time>': from_time}, extra='ORDER BY id ASC')

    for each in data:
        each['data'] = pickle.loads(each['data'])
    return data


data_collection = DataCollection()
thread = threading.Thread(target=auto_update)
thread.start()
