from unittest import mock

from fakeredis import FakeStrictRedis
from rq.queue import Queue
from rq.registry import StartedJobRegistry

import hirefire
from hirefire.procs import load_procs, loaded_procs
from tests.contrib.django.testapp.rq_test_procs import AnotherWorkerProc


class TestRQProc:

	# TODO: add proper proc unloading as part of test startup and teardown.

	def test_can_count_queues_properly(self):
		try:
			loaded_procs.clear()
			# Put some jobs on the queue
			self._add_jobs_to_queue('high', 2)
			self._add_jobs_to_queue('bottom', 4)

			# Now fake a job being active for one of them
			for idx, queue_name in enumerate(['high', 'bottom']):
				queue = Queue(queue_name, connection=FakeStrictRedis())
				registry = StartedJobRegistry(queue_name, queue.connection)
				# Passing in a negative score is important here, otherwise the job will be recognized as expired
				registry.connection.zadd(registry.key, -1, 'job_id_{}'.format(idx))

			# Load the HF procs
			procs = load_procs(*(
				'tests.contrib.django.testapp.rq_test_procs.WorkerProc',
				'tests.contrib.django.testapp.rq_test_procs.AnotherWorkerProc'
			))

			# Total should be all queued + 1 active for each
			assert sum([proc.quantity() for proc_name, proc in procs.items()]) == 8
		finally:
			loaded_procs.clear()

	def test_warns_when_queues_are_multi_assigned(self):
		try:
			loaded_procs.clear()
			# Force a queue of the same name from one proc onto the other proc.
			AnotherWorkerProc.queues.append('high')
			with mock.patch.object(hirefire.procs, 'logger') as patched_logger:
				load_procs(*(
					'tests.contrib.django.testapp.rq_test_procs.WorkerProc',
					'tests.contrib.django.testapp.rq_test_procs.AnotherWorkerProc'
				))
				patched_logger.warning.assert_called()
		finally:
			AnotherWorkerProc.queues.pop(2)
			loaded_procs.clear()

	def _add_jobs_to_queue(self, queue_name, num):
		queue = Queue(queue_name, connection=FakeStrictRedis())
		for _ in range(num):
			queue.enqueue(self._dummy_func)

	@classmethod
	def _dummy_func(cls):
		pass