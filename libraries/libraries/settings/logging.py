# logging
import os
PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE_DIR = os.path.dirname(PROJECT_DIR)
LOGGING_DIR = os.path.join(BASE_DIR, 'logs')

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'quiet_down_elasticsearch': {
            '()': 'libraries.log.QuietDownElasticsearch',
        },
        # only require_debug_false is acutally used but both are here for
        # possible future convenience
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
    },
    'formatters': {
        # django.request logging provides additional HTTP info we're interested in
        'http': {
            'format': '[{asctime}] {levelname} {name}:{lineno} {status_code} {message}',
            'datefmt': "%Y-%m-%d %H:%M:%S",
            'style': '{',
        },
        # not used
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
        'standard': {
            'format': '[{asctime}] {levelname} {name}:{lineno} {message}',
            'datefmt': "%Y-%m-%d %H:%M:%S",
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'filters': ['quiet_down_elasticsearch'],
            'formatter': 'standard',
        },
        'console_http': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'http',
        },
        'logfile': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'formatter': 'standard',
            'filename': os.path.join(LOGGING_DIR, 'all.log'),
            'filters': ['quiet_down_elasticsearch'],
        },
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
            'filters': ['require_debug_false'],
            'include_html': False,
            # Django docs are wrong, even if you have a EMAIL_BACKEND setting
            # you _have_ to specify one here to make AdminEmailHandler work
            'email_backend': 'django.core.mail.backends.smtp.EmailBackend',
        },
    },
    'loggers': {
        'django.request': {
            'handlers': ['console_http', 'logfile'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'mgmt_cmd.script': {
            'handlers': ['mail_admins', 'console'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'py.warnings': {
            'handlers': ['console', 'logfile'],
            'propagate': False,
        },
        '': {
            'handlers': ['console', 'logfile'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}
