from engine.Support.env import env

CONFIG = {
    # -------------------------------------------------------------------------
    # Default Cache Store
    # -------------------------------------------------------------------------
    # This option controls the default cache connection that gets used while
    # utilizing the Cache library. This connection is used when another
    # is not explicitly requested when executing a cache operation.
    #
    'default': env('CACHE_DRIVER', 'file'),

    # -------------------------------------------------------------------------
    # Cache Stores
    # -------------------------------------------------------------------------
    # Here you may define all of the cache "stores" for your application as
    # well as their drivers. You may even define multiple stores for the
    # same driver to group separate areas of your application.
    #
    'stores': {

        'file': {
            'driver': 'file',
            'path': 'storage/framework/cache',
        },

        'array': {
            'driver': 'array',  # In-memory volatile array for automated unit testing
        },

    },

    # -------------------------------------------------------------------------
    # Cache Key Prefix
    # -------------------------------------------------------------------------
    # When utilizing a shared cache server (like a shared redis cluster), you
    # might experience key collisions. This prefix is appended to all keys
    # to prevent application storage overlapping.
    #
    'prefix': env('CACHE_PREFIX', 'nova_cache_'),
}