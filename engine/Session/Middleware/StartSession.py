import time
from typing import Any, Callable
from engine.Support.config import config
from engine.Session.Store import Store
from engine.Session.SessionManager import SessionManager

#--------------------------------------------------------------------------
# Nova - Session Lifecycle Management Middleware
#--------------------------------------------------------------------------
#
# @package  Nova
# @author   Nova Core Team
#
# This middleware manages HTTP operations. It handles reading the initial
# client-side entry cookie token strings, matching attributes to active store
# configurations, and formatting outbound response headers securely.
#

class StartSession:

    def __init__(self, manager: SessionManager):
        """
        Create a new session lifecycle pipeline execution block.
        """
        self._manager: SessionManager = manager

    def handle(self, request: Any, next_callback: Callable) -> Any:
        """
        Intercept and execute the core session handling routine.
        """
        cookie_name = config('session.cookie.name', 'nova_session')
        
        # Extract existing session target signatures from incoming payload cookies
        session_id = request.cookies.get(cookie_name)
        
        # Instantiate active store framework map passing configured driver tracking
        driver = self._manager.driver()
        session_store = Store(cookie_name, driver, session_id)
        
        # Bind the live context container instance right onto the dynamic request object
        request.set_session(session_store)

        # Transition forward down the pipeline to execute the downstream route/controller logic
        response = next_callback(request)

        # Commit memory modifications back to structural storage nodes
        session_store.save()

        # Append tracking cookie rules back onto the outbound response metadata layout
        self._add_cookie_to_response(response, session_store)

        return response

    def _add_cookie_to_response(self, response: Any, session: Store) -> None:
        """
        Parse configurations to structuralize the response Set-Cookie headers.
        """
        cookie_config = config('session.cookie', {})
        expire_on_close = config('session.expire_on_close', False)
        
        # Compute proper baseline max-age attributes from baseline configuration arrays
        if expire_on_close:
            max_age = None
            expires = None
        else:
            lifetime_minutes = int(config('session.lifetime', 120))
            max_age = lifetime_minutes * 60
            expires = time.time() + max_age

        # Push the unified cookie layout into the dynamic Response Header map
        response.headers.set_cookie(
            key=cookie_config.get('name', 'nova_session'),
            value=session.id(),
            max_age=max_age,
            expires=expires,
            path=cookie_config.get('path', '/'),
            domain=cookie_config.get('domain'),
            secure=cookie_config.get('secure', False),
            httponly=cookie_config.get('http_only', True),
            samesite=cookie_config.get('same_site', 'lax')
        )