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
        if request.method not in self.routes:
            raise HttpError(405, 'Method Not Allowed')

        method_routes = self.routes[request.method]

        if request.path in method_routes:
            route_target = method_routes[request.path]
            
            # If the route target is a (ControllerClass, 'method_string') tuple
            if isinstance(route_target, tuple):
                controller_class, method_name = route_target
                
                # TODO: Future optimization - resolve via your DI Container
                # instead of manual instantiation so constructor injection works!
                controller_instance = controller_class()
                
                # Get the method from the instance
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