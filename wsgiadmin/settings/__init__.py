from wsgiadmin.settings.base import *
from wsgiadmin.settings.config import *

import sys
sys.path.insert(0, '/etc/pcp/')
try:
    from pcp_config import *
except ImportError:
    pass
finally:
    del sys.path[0]

try:
    from wsgiadmin.settings.local import *
except ImportError:
    pass

if GOPAY:
    INSTALLED_APPS.append('gopay4django')

if DEBUG_TOOLBAR:

    INSTALLED_APPS += ('debug_toolbar',)

    DEBUG_TOOLBAR_PANELS = (
        'debug_toolbar.panels.version.VersionDebugPanel',
        'debug_toolbar.panels.timer.TimerDebugPanel',
        'debug_toolbar.panels.settings_vars.SettingsVarsDebugPanel',
        'debug_toolbar.panels.headers.HeaderDebugPanel',
        'debug_toolbar.panels.request_vars.RequestVarsDebugPanel',
        'debug_toolbar.panels.template.TemplateDebugPanel',
        'debug_toolbar.panels.sql.SQLDebugPanel',
        'debug_toolbar.panels.signals.SignalDebugPanel',
        'debug_toolbar.panels.logger.LoggingPanel',
        )

    DEBUG_TOOLBAR_CONFIG = {
        'INTERCEPT_REDIRECTS': False,
    }

    MIDDLEWARE_CLASSES += (
        'debug_toolbar.middleware.DebugToolbarMiddleware',
    )
