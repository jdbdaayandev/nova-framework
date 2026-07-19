# app/Http/Controllers/HomeController.py
import sys
from engine.Http.request import Request
from engine.View.view import view

class HomeController:
    def index(self, request: Request):
        """
        Handles the root incoming request and renders the main landing page.
        """
        # Return the string directly. The framework's router 
        # will automatically wrap this in an HTTP Response for you!
        return view('welcome', {
            'python_version': sys.version.split()[0],
            'framework_version': 'v1.0.0-alpha',
            'env': 'Development'
        })