from hirefire.procs.celery import CeleryProc


class WorkerProc(CeleryProc):
    name = 'worker'
    queues = ['celery']
    inspect_statuses = ['active', 'reserved', 'scheduled']
