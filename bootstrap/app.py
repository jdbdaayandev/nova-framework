import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from engine.Container.container import Container
from engine.Routing.router import Router
from routes.web import register_routes

def create_app() -> Container:
    """Bootstraps the framework and returns the application container."""
    app = Container()

    # 1. Bind configuration
    app.singleton('config', lambda c: {
        'app_name': 'My Strict Python Framework',
        'env': 'local'
    })

    # 2. Bind the Router as a Singleton
    app.singleton('router', lambda c: Router())

    # 3. Load the Application Routes
    router = app.make('router')
    register_routes(router)
    
    return app