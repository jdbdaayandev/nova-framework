from engine.Support.env import env

CONFIG = {
    # -------------------------------------------------------------------------
    # Default Session Driver
    # -------------------------------------------------------------------------
    # This option controls the default session "driver" that will be used on
    # requests. By default, we use the light "file" driver which is perfect
    # for local environments.
    # Options: 'file', 'cookie', 'array' (volatile local testing memory)
    #
    'driver': env('SESSION_DRIVER', 'file'),

    # -------------------------------------------------------------------------
    # Session Lifetime
    # -------------------------------------------------------------------------
    # Here you may specify the number of minutes that you wish the session
    # to be allowed to remain idle before it expires.
    #
    'lifetime': int(env('SESSION_LIFETIME', 120)),

    # -------------------------------------------------------------------------
    # Session Expire On Close
    # -------------------------------------------------------------------------
    # This option determines whether the session should immediately expire
    # when the user closes their browser window.
    #
    'expire_on_close': False,

    # -------------------------------------------------------------------------
    # Session File Location
    # -------------------------------------------------------------------------
    # When using the native "file" session driver, the session file payloads
    # are stored on this local disk pathway. Ensure this path is writable!
    #
    'files': 'storage/framework/sessions',

    # -------------------------------------------------------------------------
    # Session Cookie Configuration
    # -------------------------------------------------------------------------
    # The information below alters the properties of the cookie assigned to the
    # client browser by Nova's core HTTP engine.
    #
    'cookie': {
        'name': env('SESSION_COOKIE_NAME', 'nova_session'),
        'path': '/',
        'domain': env('SESSION_DOMAIN', None),
        # Ensures cookies are strictly delivered over HTTPS in production
        'secure': env('SESSION_SECURE_COOKIE', False),
        # Prevents client-side scripts (JS) from intercepting the session token
        'http_only': True,
        # Defends against Cross-Site Request Forgery (CSRF) exploits
        # Options: 'lax', 'strict', 'none'
        'same_site': 'lax',
    },
}