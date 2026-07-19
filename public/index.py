# public/index.py
import os
import sys
from bootstrap.app import create_app
from engine.Http.response import Response
from engine.Http.request import Request  # Import Nova's Request parser

# Initialize the core DI Container instance
app = create_app()

def application(environ, start_response):
    path_info = environ.get('PATH_INFO', '/')

    # 1. Static Asset Router (Favicon, CSS, images)
    public_dir = os.path.dirname(os.path.abspath(__file__))
    static_file_path = os.path.join(public_dir, path_info.lstrip('/'))

    if os.path.isfile(static_file_path) and not static_file_path.endswith('.py'):
        content_type = 'text/plain'
        if static_file_path.endswith('.svg'):
            content_type = 'image/svg+xml'
        elif static_file_path.endswith('.css'):
            content_type = 'text/css'
            
        with open(static_file_path, 'rb') as f:
            content = f.read()
            
        start_response('200 OK', [('Content-Type', content_type)])
        return [content]

    # 2. Framework Core Route Dispatcher
    try:
        # Transform raw WSGI environment into Nova's Request object
        request = Request(environ)
        
        # Resolve the Router instance out of your DI Container
        router = app.make('router')
        
        # Dispatch the request through the router to match paths and methods
        if hasattr(router, 'dispatch'):
            response = router.dispatch(request)
        else:
            response = router.handle(request)
            
    except Exception as e:
        # High-level fallback catch-all for structural runtime errors
        response = Response(f"<h3>Internal Server Error</h3><p>{str(e)}</p>", status=500)

    # 3. HTTP Headers Translation
    status = response.status_string 
    headers = list(response.headers.items()) 

    start_response(status, headers)
    return [response.content.encode('utf-8')]