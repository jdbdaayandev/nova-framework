import os
import sys
import mimetypes

# 1. Boot Environment with absolute root directory safety
# (Prevents environment loading failures if server is executed from deep child directories)
PUBLIC_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_PATH = os.path.dirname(PUBLIC_DIR)

if ROOT_PATH not in sys.path:
    sys.path.insert(0, ROOT_PATH)

from engine.Support.env import load_env, env
load_env(os.path.join(ROOT_PATH, '.env'))

# 2. Bootstrap Core
from bootstrap.app import create_app
from engine.Http.request import Request
from engine.Http.response import Response
from engine.Exceptions.handler import ErrorHandler

# Initialize DI Container
app = create_app()

def serve_static(path_info, start_response):
    """
    Attempts to serve a static asset out of the public folder directory tree. 
    Returns the WSGI payload if found, otherwise returns None.
    """
    file_path = os.path.join(PUBLIC_DIR, path_info.lstrip('/'))

    # Security Guard: Ensure execution targets files and blocks internal script exposure
    if os.path.isfile(file_path) and not file_path.endswith('.py'):
        mime_type, _ = mimetypes.guess_type(file_path)
        content_type = mime_type or 'text/plain'
        
        with open(file_path, 'rb') as f:
            content = f.read()
            
        start_response('200 OK', [('Content-Type', content_type)])
        return [content]
        
    return None

def application(environ, start_response):
    """
    The main WSGI Front Controller engine execution loop.
    """
    path_info = environ.get('PATH_INFO', '/')

    # 1. Intercept Static Assets
    static_response = serve_static(path_info, start_response)
    if static_response:
        return static_response

    # 2. Process Framework Request Pipeline
    try:
        request = Request(environ)
        router = app.make('router')
        
        # Polymorphic Dispatch resolution hook
        if hasattr(router, 'dispatch'):
            response = router.dispatch(request)
        else:
            response = router.handle(request)
            
        # 🚀 Fix: Intercept clean HTTP error returns (404, 403, etc.) that didn't throw exceptions
        response = ErrorHandler.handle_error_response(response)
            
    except Exception as e:
        # 🚀 Handle runtime crashes, component failures, and HttpErrors
        response = ErrorHandler.handle_exception(e)

    # 3. Format and Send HTTP Response Headers
    headers = list(response.headers.items()) if isinstance(response.headers, dict) else response.headers
    
    # Standardize status format to avoid wsgiref library type strictness crashes
    status_line = getattr(response, 'status_string', None)
    if not status_line:
        status_code = getattr(response, 'status', 200)
        # Handle string or numerical input safely
        if isinstance(status_code, int):
            status_map = {200: "200 OK", 403: "403 Forbidden", 404: "404 Not Found", 500: "500 Internal Server Error"}
            status_line = status_map.get(status_code, f"{status_code} Error")
        else:
            status_line = str(status_code)

    start_response(status_line, headers)
    
    # 4. Stream Content Payload Binary Data
    if isinstance(response.content, bytes):
        return [response.content]
        
    return [str(response.content).encode('utf-8')]