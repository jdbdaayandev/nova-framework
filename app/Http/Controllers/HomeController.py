import sys
from engine.Http.request import Request
from engine.View.view import view
from engine.Support.env import env

class HomeController:
    def index(self, request: Request):
        """
        Handles the root incoming request and renders the main landing page.
        """
        return view('welcome', {
            'python_version': sys.version.split()[0],
            'framework_version': 'v1.0.0-alpha',
            'env': env('APP_ENV', 'production').capitalize() 
        })