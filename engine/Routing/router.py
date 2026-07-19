import os
import mimetypes
import inspect
from typing import Callable, Dict, Any, Tuple, Union, List, Optional
from engine.Http.request import Request
from engine.Http.response import Response

class HttpError(Exception):
    def __init__(self, status_code: int, message: str):
        self.status_code = status_code
        self.message = message

class Router:
    # --------------------------------------------------------------------------
    # Middleware Routing Registries
    # --------------------------------------------------------------------------
    # Global middleware stacks running sequentially on EVERY dynamic web request
    _global_middleware: List[str] = [
        'engine.Session.Middleware.StartSession',
    ]

    # Map named shortcuts/aliases to their absolute Python class locations
    _middleware_aliases: Dict[str, str] = {
        'auth': 'app.Http.Middleware.Authenticate',
        'guest': 'app.Http.Middleware.RedirectIfAuthenticated',
    }

    def __init__(self, app: Optional[Any] = None):
        self._app = app
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
        """
        Universal dispatch gateway intercepted directly by the Front Controller.
        """
        # 1. INTERCEPT STATIC FILES (Preserved)
        if request.path.startswith('/public/') and request.method == 'GET':
            return self._serve_static_file(request.path)

        # 2. VALIDATE HTTP ROUTE EXISTENCE
        if request.method not in self.routes:
            raise HttpError(405, 'Method Not Allowed')

        method_routes = self.routes[request.method]
        if request.path not in method_routes:
            raise HttpError(404, 'Page Not Found')

        route_target = method_routes[request.path]

        # 3. BUILD THE MIDDLEWARE ONION PIPELINE
        # We compile global and route/controller specific middleware layers into a unified stack
        middleware_instances = self._resolve_global_middleware()
        
        # If targeting a controller method, extract its custom internal middleware layers
        if isinstance(route_target, tuple):
            controller_class, method_name = route_target
            controller_instance = controller_class()
            
            # Extract out conditionally matching controller-level middleware
            if hasattr(controller_instance, 'get_middleware_for_method'):
                active_aliases = controller_instance.get_middleware_for_method(method_name)
                middleware_instances.extend(self._resolve_route_middleware(active_aliases))
                
            # Define final callback target execution
            def final_destination(req: Request) -> Response:
                handler = getattr(controller_instance, method_name)
                return self._execute_handler(handler, req)
        else:
            # Simple closure/anonymous function route target
            def final_destination(req: Request) -> Response:
                return self._execute_handler(route_target, req)

        # 4. IGNITE THE ONION LAYER PIPELINE PIPING PROCESS
        pipeline = self._build_pipeline(middleware_instances, final_destination)
        return pipeline(request)

    # --------------------------------------------------------------------------
    # Core Pipeline Composers & Resolvers
    # --------------------------------------------------------------------------
    def _build_pipeline(self, middlewares: List[Any], destination: Callable[[Request], Response]) -> Callable[[Request], Response]:
        """
        Assembles a classic nested onion-layered middleware callback string execution matrix.
        """
        def pipeline_core(request: Request) -> Response:
            def next_layer(index: int) -> Callable[[Request], Response]:
                def call_middleware(req: Request) -> Response:
                    if index >= len(middlewares):
                        return destination(req)
                    # Pass the request context and the handle trailing down into the next index tier
                    return middlewares[index].handle(req, next_layer(index + 1))
                return call_middleware
            return next_layer(0)(request)
        return pipeline_core

    def _resolve_global_middleware(self) -> List[Any]:
        """Resolves system level base global middleware strings into actionable objects."""
        return [self._instantiate_middleware(path) for path in self._global_middleware]

    def _resolve_route_middleware(self, aliases: List[str]) -> List[Any]:
        """Resolves short-hand named route/controller middleware string flags."""
        instances = []
        for alias in aliases:
            path = self._middleware_aliases.get(alias, alias)
            instances.append(self._instantiate_middleware(path))
        return instances

    def _instantiate_middleware(self, middleware_path: str) -> Any:
        """Dynamically imports and boots classes directly out of runtime matrices."""
        module_name, class_name = middleware_path.rsplit('.', 1)
        module = __import__(module_name, fromlist=[class_name])
        middleware_class = getattr(module, class_name)
        
        # Inject context references if IoC structural container components are available
        if self._app and hasattr(self._app, 'has') and self._app.has('session'):
            return middleware_class(self._app.make('session'))
        return middleware_class()

    def _execute_handler(self, handler: Callable, request: Request) -> Response:
        """
        Inspects parameters and safely invokes target endpoints.
        """
        sig = inspect.signature(handler)
        if len(sig.parameters) > 0:
            result = handler(request)
        else:
            result = handler()
            
        if isinstance(result, Response):
            return result
        return Response(str(result))

    def _serve_static_file(self, path: str) -> Response:
        """Reads a static file from disk and returns an HTTP response."""
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        clean_path = path.lstrip('/')
        file_path = os.path.abspath(os.path.join(base_dir, clean_path))

        public_dir = os.path.abspath(os.path.join(base_dir, 'public'))
        if not file_path.startswith(public_dir):
            raise HttpError(403, 'Forbidden')

        if not os.path.exists(file_path) or not os.path.isfile(file_path):
            raise HttpError(404, 'Static File Not Found')

        content_type, _ = mimetypes.guess_type(file_path)
        content_type = content_type or 'application/octet-stream'

        with open(file_path, 'rb') as f:
            content = f.read()

        return Response(content, headers=[('Content-Type', content_type)])