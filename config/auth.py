from engine.Support.env import env

CONFIG = {
    # -------------------------------------------------------------------------
    # Authentication Defaults
    # -------------------------------------------------------------------------
    # This option controls the default authentication "guard" and password
    # reset options for your application. You may change these defaults
    # as required, but they're a perfect start for most apps.
    #
    'defaults': {
        'guard': env('AUTH_GUARD', 'web'),
        'provider': 'users',
    },

    # -------------------------------------------------------------------------
    # Authentication Guards
    # -------------------------------------------------------------------------
    # Next, you may define every authentication guard for your application.
    # All authentication guards have a user provider. This defines how the
    # users are actually retrieved out of your database storage engines.
    #
    'guards': {

        'web': {
            'driver': 'session',
            'provider': 'users',
        },

        'api': {
            'driver': 'token',
            'provider': 'users',
            'input_key': 'api_token',  # Looks for ?api_token= or HTTP Bearer tokens
        },

    },

    # -------------------------------------------------------------------------
    # User Providers
    # -------------------------------------------------------------------------
    # All authentication guards have a user provider. This defines how the
    # users are actually retrieved out of your databases. If you have
    # multiple user tables you may configure multiple providers.
    #
    'providers': {

        'users': {
            'driver': 'orm',
            'model': 'app.Models.User.User',  # Path pointing directly to Nova ORM class
            'table': 'users',
        },

    },
}