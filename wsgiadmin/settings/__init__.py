from wsgiadmin.settings.base import *
from wsgiadmin.settings.config import *

try:
    from wsgiadmin.settings.local import *
except ImportError:
    pass

try:
    from wsgiadmin.settings.prod import *
except ImportError:
    pass

#logging.basicConfig(level=logging.INFO, filename=ROOT + 'rosti.log',
#                    format='%(asctime)s %(levelname)s %(message)s')

DEBUG_TOOLBAR = False
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
