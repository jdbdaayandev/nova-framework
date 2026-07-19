# File: bootstrap/app.py
import os
from engine.Container.container import Container
from engine.Routing.router import Router
from engine.Support.env import load_env
from engine.Support.config import ConfigRepository

def create_app():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # 1. Boot Environment Variables
    load_env(os.path.join(base_dir, '.env'))
    
    # 2. Boot Configuration Repository (Triggers our updated importlib scanner)
    ConfigRepository.load_from_directory(os.path.join(base_dir, 'config'))
    
    container = Container.getInstance()
    container.singleton('router', lambda c: Router())
    
    import routes.web as web_routes
    web_routes.register_routes(container.make('router'))
    
    return container