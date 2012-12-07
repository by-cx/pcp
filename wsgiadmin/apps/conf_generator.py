"""
All these class should return dict in this format:

{
    "nginx_vhost"
    "apache_vhost"
    "supervisor_conf"
}
"""

class StaticConfig(object):
    def __init__(self, app):
        self.app = app


class PHPConfig(object):
    def __init__(self, app):
        self.app = app


class uWSGIConfig(object):
    def __init__(self, app):
        self.app = app


class NativeConfig(object):
    def __init__(self, app):
        self.app = app


class ProxyConfig(object):
    def __init__(self, app):
        self.app = app
