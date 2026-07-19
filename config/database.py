from engine.Support.env import env

CONFIG = {
    # -------------------------------------------------------------------------
    # Default Database Connection Name
    # -------------------------------------------------------------------------
    # Here you may specify which of the database connections below you wish
    # to use as your default connection for all database work. Of course
    # you may use many connections at once using the Database library.
    #
    'default': env('DB_CONNECTION', 'sqlite'),

    # -------------------------------------------------------------------------
    # Database Connections
    # -------------------------------------------------------------------------
    # Here are each of the database connections setup for your application.
    # Of course, examples of configuring each database platform that is
    # supported by Nova is shown below to make development simple.
    #
    # All database work in Nova is done through the native Python DB-API.
    #
    'connections': {

        'sqlite': {
            'driver': 'sqlite',
            'database': env('DB_DATABASE', 'database/database.sqlite'),
            'foreign_key_constraints': True,
        },

        'mysql': {
            'driver': 'mysql',
            'host': env('DB_HOST', '127.0.0.1'),
            'port': int(env('DB_PORT', 3306)),
            'database': env('DB_DATABASE', 'nova'),
            'username': env('DB_USERNAME', 'root'),
            'password': env('DB_PASSWORD', None),
            'charset': 'utf8mb4',
        },

        'postgresql': {
            'driver': 'postgresql',
            'host': env('DB_HOST', '127.0.0.1'),
            'port': int(env('DB_PORT', 5432)),
            'database': env('DB_DATABASE', 'nova'),
            'username': env('DB_USERNAME', 'postgres'),
            'password': env('DB_PASSWORD', None),
            'schema': 'public',
        },

    },

    # -------------------------------------------------------------------------
    # Migration Repository Table
    # -------------------------------------------------------------------------
    # This table keeps track of all the migrations that have already run for
    # your application. Using this information, we can determine which of
    # the migrations on disk haven't actually been run in the database.
    #
    'migrations': 'migrations',
}