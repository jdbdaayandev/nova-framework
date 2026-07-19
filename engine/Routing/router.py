import os
import mimetypes
import inspect
from typing import Callable, Dict, Any, Tuple, Union
from engine.Http.request import Request
from engine.Http.response import Response

class HttpError(Exception):
    def __init__(self, status_code: int, message: str):
        self.status_code = status_code
        self.message = message

class Router:
    def __init__(self):
        # Maps HTTP verbs to paths and their respective handlers
        self.routes: Dict[str, Dict[str, Union[Callable, Tuple]]] = {
            'GET': {}, 'POST': {}, 'PUT': {}, 'DELETE': {}
        }

    def get(self, path: str, handler: Union[Callable, Tuple]):
        self.routes['GET'][path] = handler

    def post(self, path: str, handler: Union[Callable, Tuple]):
        self.routes['POST'][path] = handler

    def put(self, path: str, handler: Union[Callable, Tuple]):
        self.routes['PUT'][path] = handler

    def delete(self, path: str, handler: Union[Callable, Tuple]):
        self.routes['DELETE'][path] = handler

    def dispatch(self, request: Request) -> Response:
        # 1. INTERCEPT STATIC FILES
        if request.path.startswith('/public/') and request.method == 'GET':
            return self._serve_static_file(request.path)

        # 2. STANDARD ROUTING
        if request.method not in self.routes:
            raise HttpError(405, 'Method Not Allowed')

        method_routes = self.routes[request.method]

        if request.path in method_routes:
            route_target = method_routes[request.path]
            
            # If the route target is a (ControllerClass, 'method_string') tuple
            if isinstance(route_target, tuple):
                controller_class, method_name = route_target
                controller_instance = controller_class()
                handler = getattr(controller_instance, method_name)
            else:
                # It's a standard closure/function
                handler = route_target
            
            # Inspect parameters to safely pass the request object if requested
            sig = inspect.signature(handler)
            if len(sig.parameters) > 0:
                result = handler(request)
            else:
                result = handler()
            
            # Ensure we return a clean Framework Response object
            if isinstance(result, Response):
                return result
            return Response(str(result))

        raise HttpError(404, 'Page Not Found')

    def _serve_static_file(self, path: str) -> Response:
        """Reads a static file from disk and returns an HTTP response."""
        # Find project root (3 levels up: engine/Routing/router.py -> project_root)
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        
        # Strip the leading slash from the path so os.path.join doesn't treat it as absolute
        # Example: '/public/logo.svg' -> 'public/logo.svg'
        clean_path = path.lstrip('/')
        file_path = os.path.abspath(os.path.join(base_dir, clean_path))

        # Security check: Prevent directory traversal attacks (e.g., /public/../../etc/passwd)
        public_dir = os.path.abspath(os.path.join(base_dir, 'public'))
        if not file_path.startswith(public_dir):
            raise HttpError(403, 'Forbidden')

        if not os.path.exists(file_path) or not os.path.isfile(file_path):
            raise HttpError(404, 'Static File Not Found')

        # Guess the MIME type (e.g., 'image/svg+xml' or 'text/css')
        content_type, _ = mimetypes.guess_type(file_path)
        content_type = content_type or 'application/octet-stream'

        # Read the file as binary (required for images, works fine for text files)
        with open(file_path, 'rb') as f:
            content = f.read()

        return Response(content, headers=[('Content-Type', content_type)])