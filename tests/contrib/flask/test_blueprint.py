"""Tests for the Flask blueprint factory."""

from http import HTTPStatus

import pytest

from flask import Flask


@pytest.fixture
def flask_app():
    """A Flask application instance."""

    app = Flask(__name__)
    app.testing = True

    return app


@pytest.mark.parametrize(
    "token, status_code",
    (("test", HTTPStatus.OK), ("garbage", HTTPStatus.NOT_FOUND))
)
def test_hirefire_info(flask_app, monkeypatch, token, status_code):
    """Enforce the presence of the HireFire token in the info endpoint path."""

    # Patch over load_procs() and dump_procs() so we don't have to worry about
    # specifying actual Proc subclasses when we construct the test blueprint.
    monkeypatch.setattr("hirefire.procs.load_procs", lambda *args: args)
    monkeypatch.setattr("hirefire.procs.dump_procs", lambda arg: {})
    
    from hirefire.contrib.flask.blueprint import build_hirefire_blueprint

    # Normally, the second argument would be a list of Proc subclasses. We can
    # pass a garbage string because we patched over load_procs() and
    # dump_procs()
    flask_app.register_blueprint(build_hirefire_blueprint("test", ("proc",)))
    
    with flask_app.test_client() as client:
        response = client.get(f"/hirefire/{token}/info")

    assert response.status_code == status_code
