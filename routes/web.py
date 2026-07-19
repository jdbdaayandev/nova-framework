# routes/web.py
import sys
from engine.Routing.router import Router
from engine.View.view import view
from app.Http.Controllers.HomeController import HomeController

def register_routes(router: Router):
    
    # 1. Define the welcome function (optional helper, or kept for reference)
    def welcome():
        return view('welcome', {
            'python_version': sys.version.split()[0],
            'framework_version': 'v1.0.0-alpha',
            'env': 'Development'
        })

    # 2. Corrected Indentation: Aligned perfectly to 4 spaces
    router.get('/', (HomeController, 'index'))

    # Your other existing routes remain down here:
    # router.post('/users', (UserController, 'store'))