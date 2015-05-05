from __future__ import absolute_import
import re

import tornado.web

from hirefire.procs import load_procs, dump_procs, HIREFIRE_FOUND


__all__ = ['hirefire_handlers']


def hirefire_handlers(token, procs):
    if not procs:
        raise Exception('The HireFire Tornado handler '
                        'requires at least one proc defined.')
    test_path = r'^/hirefire/test/?$'
    info_path = r'^/hirefire/%s/info/?$' % re.escape(token)
    HireFireInfoHandler.loaded_procs = load_procs(*procs)
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
        self.write(HIREFIRE_FOUND)
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
    loaded_procs = []

    def info(self):
        """
        The heart of the app, returning a JSON ecoded list
        of proc results.
        """
        # do the JSON dumping ourselves to be able to handle datetimes nicely
        payload = dump_procs(self.loaded_procs).replace("</", "<\\/")
        self.set_header("Content-Type", "application/json; charset=UTF-8")
        self.write(payload)
        self.finish()

    def get(self):
        self.info()

    def post(self):
        self.info()
