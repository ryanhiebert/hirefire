from hirefire.procs.rq import RQProc
from fakeredis import FakeStrictRedis
from rq import Queue


class WorkerProc(RQProc):
    name = 'worker'
    queues = ['high', 'low']
    connection = FakeStrictRedis()


class AnotherWorkerProc(RQProc):
    name = 'double_dipping_worker'
    queues = ['top', 'bottom']
    connection = FakeStrictRedis()
