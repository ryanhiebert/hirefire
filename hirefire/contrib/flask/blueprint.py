from __future__ import absolute_import

from flask import Blueprint, Response

from hirefire.procs import load_procs, dump_procs, HIREFIRE_FOUND


__all__ = ['build_hirefire_blueprint']


def build_hirefire_blueprint(token, procs):
    """
    The Flask middleware provided as a Blueprint exposing the the URL paths
    HireFire requires. Implements the test response and the json response
    that contains the procs data.
    """
    if not procs:
        raise RuntimeError('At least one proc should be passed')
    loaded_procs = load_procs(*procs)
    bp = Blueprint(__name__, 'hirefire')

    @bp.route('/hirefire/test')
    def test():
        """
        Doesn't do much except telling the HireFire bot it's installed.
        """
        return HIREFIRE_FOUND

    @bp.route('/hirefire/<id>/info')
    def info(id):
        """
        The heart of the app, returning a JSON ecoded list
        of proc results.
        """
        return Response(dump_procs(loaded_procs), mimetype='application/json')

    return bp
