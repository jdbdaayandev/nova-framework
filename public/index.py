import os
import mimetypes

# 1. Boot Environment
from engine.Support.env import load_env
load_env()

# 2. Bootstrap Core
from bootstrap.app import create_app
from engine.Http.request import Request
from engine.Http.response import Response

# Initialize DI Container and define the public path
app = create_app()
PUBLIC_DIR = os.path.dirname(os.path.abspath(__file__))

def serve_static(path_info, start_response):
    """
    Attempts to serve a static asset. 
    Returns the WSGI payload if found, otherwise returns None.
    """
    file_path = os.path.join(PUBLIC_DIR, path_info.lstrip('/'))

    if os.path.isfile(file_path) and not file_path.endswith('.py'):
        # Dynamically guess the mimetype (e.g., image/svg+xml, text/css)
        mime_type, _ = mimetypes.guess_type(file_path)
        content_type = mime_type or 'text/plain'
        
        with open(file_path, 'rb') as f:
            content = f.read()
            
        start_response('200 OK', [('Content-Type', content_type)])
        return [content]
        
    return None

def application(environ, start_response):
    """
    The main WSGI Front Controller.
    """
    path_info = environ.get('PATH_INFO', '/')

    # 1. Intercept Static Assets
    static_response = serve_static(path_info, start_response)
    if static_response:
        return static_response

    # 2. Process Framework Request
    try:
        request = Request(environ)
        router = app.make('router')
        
        # Dispatch through the router
        if hasattr(router, 'dispatch'):
            response = router.dispatch(request)
        else:
            response = router.handle(request)
            
    except Exception as e:
        # Fallback for structural runtime errors
        response = Response(f"<h3>Internal Server Error</h3><p>{str(e)}</p>", status=500)

    # 3. Send HTTP Response
    start_response(response.status_string, list(response.headers.items()))
    return [response.content.encode('utf-8')]