from typing import Any, Callable, Dict, List
from engine.Http.request import Request

class Kernel:
    """
    The HTTP Lifecycle Kernel.
    
    Orchestrates the sequential application of global pipelines and converts 
    middleware string aliases into executable instance containers.
    """

    # Global middlewares executed sequentially on EVERY incoming web request
    _middleware: List[str] = [
        'engine.Session.Middleware.StartSession',
    ]

    # Map aliases to their fully qualified path names
    _route_middleware: Dict[str, str] = {
        'auth': 'app.Http.Middleware.Authenticate',
        'guest': 'app.Http.Middleware.RedirectIfAuthenticated',
    }

    def __init__(self, app: Any) -> None:
        self._app: Any = app

    def gather_global_middleware(self) -> List[Any]:
        """Resolves all global middleware paths into execution ready instances."""
        return [self._resolve_middleware(path) for path in self._middleware]

    def gather_controller_middleware(self, aliases: List[str]) -> List[Any]:
        """Resolves specific controller level named middleware string aliases."""
        instances = []
        for alias in aliases:
            path = self._route_middleware.get(alias, alias)
            instances.append(self._resolve_middleware(path))
        return instances

    def build_pipeline(self, middlewares: List[Any], destination: Callable) -> Callable:
        """
        Constructs an onion-layered nested callback execution sequence matrix.
        """
        def pipeline_core(request: Request) -> Any:
            def next_layer(index: int) -> Callable:
                def call_middleware(req: Request) -> Any:
                    if index >= len(middlewares):
                        return destination(req)
                    return middlewares[index].handle(req, next_layer(index + 1))
                return call_middleware
            return next_layer(0)(request)
        return pipeline_core

    def _resolve_middleware(self, middleware_path: str) -> Any:
        """
        Dynamically imports and instantiates code blocks directly via the container.
        """
        module_name, class_name = middleware_path.rsplit('.', 1)
        module = __import__(module_name, fromlist=[class_name])
        mw_class = getattr(module, class_name)
        
        # Inject framework resources if available
        if hasattr(self._app, 'make') and self._app.has('session'):
            return mw_class(self._app.make('session'))
            
        return mw_class()