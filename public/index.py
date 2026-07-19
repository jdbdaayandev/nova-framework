import mimetypes
import os
import sys
from http import HTTPStatus
from typing import Any, Callable, List, Optional

#--------------------------------------------------------------------------
# Nova - A Zero-Dependency Python MVC Framework
#--------------------------------------------------------------------------
#
# @package  Nova
# @author   Nova Core Team
#
# The Front Controller serves as the universal gateway for all incoming
# HTTP requests entering the application. Every request lifecycle is
# orchestrated through this single file before dispatching to routes.
#

#--------------------------------------------------------------------------
# Boot Environment & Path Guardrails
#--------------------------------------------------------------------------
#
# To prevent structural environment loading failures when executing the
# WSGI runner from deeply nested child directories, we calculate the
# absolute directory root and inject it directly into the system path matrix.
#
PUBLIC_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_PATH = os.path.dirname(PUBLIC_DIR)

if ROOT_PATH not in sys.path:
    sys.path.insert(0, ROOT_PATH)

from engine.Support.env import load_env
load_env(os.path.join(ROOT_PATH, '.env'))

#--------------------------------------------------------------------------
# Illuminate The Application Core
#--------------------------------------------------------------------------
#
# Here, we instantiate the primary framework Application instance. This
# component serves as the central Inversion of Control (IoC) Dependency
# Injection container, binding services and managing component life scopes.
#
from bootstrap.app import create_app
from engine.Http.request import Request
from engine.Exceptions.handler import ErrorHandler

app = create_app()

#--------------------------------------------------------------------------
# Serve Static Assets Interceptor
#--------------------------------------------------------------------------
#
# Before executing heavy dynamic routing cycles, we attempt to isolate
# and resolve requests pointing to physical asset files inside the public
# tree. Strict boundary validation blocks path traversal attacks.
#
def serve_static(path_info: str, start_response: Callable) -> Optional[List[bytes]]:
    """
    Safely resolves and streams requested public folder asset binaries.
    """
    target_path = os.path.abspath(os.path.join(PUBLIC_DIR, path_info.lstrip('/')))

    # Security validation pipeline:
    # 1. Enforce physical existence check on disk.
    # 2. Confirm target resides strictly inside the public folder root.
    # 3. Suppress network visibility of dynamic engine scripts (.py).
    if (
        os.path.isfile(target_path)
        and target_path.startswith(PUBLIC_DIR)
        and not target_path.endswith('.py')
    ):
        mime_type, _ = mimetypes.guess_type(target_path)
        content_type = mime_type or 'application/octet-stream'

        with open(target_path, 'rb') as asset:
            content = asset.read()

        headers = [
            ('Content-Type', content_type),
            ('Content-Length', str(len(content)))
        ]
        start_response('200 OK', headers)
        return [content]

    return None

#--------------------------------------------------------------------------
# Run The Application (WSGI Kernel Loop)
#--------------------------------------------------------------------------
#
# The universal application loop captures the raw server environment array.
# The payload transitions from a parsed Request object through a unified
# routing pipeline, emerging as a fully standardized binary Response stream.
#
def application(environ: dict[str, Any], start_response: Callable) -> List[bytes]:
    """
    Primary execution kernel interface invoked by the WSGI application server.
    """
    path_info = environ.get('PATH_INFO', '/')

    # Phase 1: Intercept asset pathways
    static_response = serve_static(path_info, start_response)
    if static_response is not None:
        return static_response

    # Phase 2: Handle routing and component dispatching
    try:
        request = Request(environ)
        router = app.make('router')

        # Polymorphic router compatibility check
        if hasattr(router, 'dispatch'):
            response = router.dispatch(request)
        else:
            response = router.handle(request)

        # Intercept explicit error returns (e.g., manual 404/403 states)
        response = ErrorHandler.handle_error_response(response)

    except Exception as exception:
        # Intercept unhandled core crashes and render layout diagnostics
        response = ErrorHandler.handle_exception(exception)

    # Phase 3: Compile and structuralize HTTP response headers
    headers = list(response.headers.items()) if isinstance(response.headers, dict) else response.headers

    # Phase 4: Enforce strict WSGI status line compatibility strings
    status_line = getattr(response, 'status_string', None)
    if not status_line:
        status_code = getattr(response, 'status', 200)
        if isinstance(status_code, int):
            try:
                http_status = HTTPStatus(status_code)
                status_line = f"{http_status.value} {http_status.phrase}"
            except ValueError:
                status_line = f"{status_code} Unknown Status"
        else:
            status_line = str(status_code)

    start_response(status_line, headers)

    # Phase 5: Emit the binary packet payload back to the web daemon
    if isinstance(response.content, bytes):
        return [response.content]

    return [str(response.content).encode('utf-8')]