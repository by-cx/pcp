from wsgiadmin.apps.backend.main import AppBackend
from wsgiadmin.apps.backend.php import PHPApp, PHPFPMApp
from wsgiadmin.apps.backend.python import PythonApp, PythonGunicornApp
from wsgiadmin.apps.backend.static import StaticApp
from wsgiadmin.apps.backend.node import NodeApp

__author__ = 'cx'


def typed_object(app):
    if app.app_type in ("uwsgi", "python"):
        app = PythonApp.objects.get(id=app.id)
    elif app.app_type == "gunicorn":
        app = PythonGunicornApp.objects.get(id=app.id)
    elif app.app_type == "php":
        app = PHPApp.objects.get(id=app.id)
    elif app.app_type == "phpfpm":
        app = PHPFPMApp.objects.get(id=app.id)
    elif app.app_type == "static":
        app = StaticApp.objects.get(id=app.id)
    elif app.app_type == "node":
        app = NodeApp.objects.get(id=app.id)
    else:
        app = AppBackend.objects.get(id=app.id)
    return app
