from engine.Support.env import env

CONFIG = {
    # -------------------------------------------------------------------------
    # Default Mailer
    # -------------------------------------------------------------------------
    # This option controls the default mailer that is used to send any email
    # messages originated by your application.
    # Options: 'smtp', 'sendmail', 'log' (writes mail bodies directly to files)
    #
    'default': env('MAIL_MAILER', 'log'),

    # -------------------------------------------------------------------------
    # Mailer Configurations
    # -------------------------------------------------------------------------
    # Here you may configure all of the mailers used by your application plus
    # their respective transports. Nova includes absolute support for standard
    # SMTP networks out of the box.
    #
    'mailers': {

        'smtp': {
            'transport': 'smtp',
            'host': env('MAIL_HOST', 'smtp.mailtrap.io'),
            'port': int(env('MAIL_PORT', 2525)),
            'encryption': env('MAIL_ENCRYPTION', 'tls'),  # Options: 'ssl', 'tls', None
            'username': env('MAIL_USERNAME', None),
            'password': env('MAIL_PASSWORD', None),
            'timeout': None,
        },

        'sendmail': {
            'transport': 'sendmail',
            'path': '/usr/sbin/sendmail -bs',
        },

        'log': {
            'transport': 'log',
            'channel': 'mail_log',
        },

    },

    # -------------------------------------------------------------------------
    # Global "From" Address Identity
    # -------------------------------------------------------------------------
    # You may wish for all e-mails sent by your application to be sent from
    # the same address. Here, you may specify a name and address that is
    # used globally for all e-mails that are sent by Nova.
    #
    'from': {
        'address': env('MAIL_FROM_ADDRESS', 'hello@example.com'),
        'name': env('MAIL_FROM_NAME', 'Nova Application System'),
    },
}