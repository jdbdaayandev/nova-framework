from engine.Support.env import env

CONFIG = {
    # -------------------------------------------------------------------------
    # Default Log Channel Name
    # -------------------------------------------------------------------------
    # This option defines the default log channel that gets written to when
    # writing messages to the logger. This constant must match one of the
    # channels defined within the "channels" dictionary array mapping below.
    #
    'default': env('LOG_CHANNEL', 'stack'),

    # -------------------------------------------------------------------------
    # Log Channels
    # -------------------------------------------------------------------------
    # Here you may configure the log channels for your application. Nova
    # utilizes the native Python "logging" utility architecture underneath to 
    # track events, errors, and framework diagnostic updates.
    #
    'channels': {

        'stack': {
            'driver': 'stack',
            'channels': ['single', 'console'],  # Dispatches logs to multiple targets simultaneously
        },

        'single': {
            'driver': 'single',
            'path': 'storage/logs/nova.log',
            'level': env('LOG_LEVEL', 'debug'),
        },

        'daily': {
            'driver': 'daily',
            'path': 'storage/logs/nova.log',
            'level': env('LOG_LEVEL', 'debug'),
            'days': 14,  # Automatically rotates logs, keeping only the last 14 days
        },

        'console': {
            'driver': 'console',
            'level': 'debug',
        },

    },
}