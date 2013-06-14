import json
import os
import re

import tornado.web

from hirefire import __version__ as hirefire_version, procs

from ..utils import TimeAwareJSONEncoder

__all__ = ['hirefire_handlers']


def setting(name, default=None):
    return os.environ.get(name) or default


TOKEN = setting('HIREFIRE_TOKEN', 'development')
PROCS = setting('HIREFIRE_PROCS', [])


def hirefire_handlers(procs):
    if not procs:
     raise Exception('The HireFire Tornado handler '
                     'requires at least one proc defined.')

    global PROCS
    PROCS = procs

    test_path = r'^/hirefire/test/?$'
    info_path = r'^/hirefire/%s/info/?$' % re.escape(TOKEN)
    handlers = [
        (test_path, HireFireTestHandler),
        (info_path, HireFireInfoHandler)
    ]
    return handlers


class HireFireTestHandler(tornado.web.RequestHandler):
    """
    RequestHandler that implements the test response.
    """
    def test(self):
        """
        Doesn't do much except telling the HireFire bot it's installed.
        """
        self.write('HireFire Handler Found!')
        self.finish()

    def get(self):
        self.test()

    def post(self):
        self.test()


class HireFireInfoHandler(tornado.web.RequestHandler):
    """
    RequestHandler that implements the json response that contains the procs
    data.
    """
    loaded_procs = procs.load_procs(*PROCS)

    def info(self):
        """
        The heart of the app, returning a JSON ecoded list
        of proc results.
        """
        data = []
        for name, proc in self.loaded_procs.items():
            data.append({
                'name': name,
                'quantity': proc.quantity() or 'null',
            })
        payload = json.dumps(data, cls=TimeAwareJSONEncoder, ensure_ascii=False)
        self.write(payload)
        self.finish()

    def get(self):
        self.info()

    def post(self):
        self.info()
