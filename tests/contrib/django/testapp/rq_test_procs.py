from hirefire.procs.rq import RQProc
from redis import Redis
# from fakeredis import FakeStrictRedis
from rq import Queue


class WorkerProc(RQProc):
    name = 'worker'
    queues = ['high', 'low']
    connection = Redis()


class AnotherWorkerProc(RQProc):
    name = 'double_dipping_worker'
    queues = ['top', 'bottom']
    connection = Redis()
