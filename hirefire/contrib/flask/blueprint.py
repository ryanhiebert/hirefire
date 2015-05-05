"""
The Flask middleware provided as a Blueprint exposing the the URL paths
HireFire requires. Implements the test response and the json response
that contains the procs data.
"""

from __future__ import absolute_import
from flask import Blueprint, Response, current_app
import json

from hirefire.procs import load_procs
from hirefire.utils import TimeAwareJSONEncoder


def build_hirefire_blueprint(token, procs):
    if not procs:
        raise RuntimeError('At least one proc should be passed')
    loaded_procs = load_procs(*procs)
    bp = Blueprint(__name__, 'hirefire')

    @bp.route('/hirefire/test/')
    def test():
        """
        Doesn't do much except telling the HireFire bot it's installed.
        """
        return 'HireFire Middleware Found!'


    @bp.route('/hirefire/<id>/info')
    def info(id):
        """
        The heart of the app, returning a JSON ecoded list
        of proc results.
        """
        data = []
        for name, proc in loaded_procs.items():
            data.append({
                'name': name,
                'quantity': proc.quantity() or 'null',
            })
        payload = json.dumps(data, cls=TimeAwareJSONEncoder, ensure_ascii=False)
        return Response(payload, mimetype='application/json')

    return bp
