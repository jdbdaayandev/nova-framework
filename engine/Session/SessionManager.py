import os
from typing import Any, Dict
from engine.Support.config import config
from engine.Session.Store import Store
from engine.Session.Drivers.FileSessionDriver import FileSessionDriver
from engine.Session.Drivers.DatabaseSessionDriver import DatabaseSessionDriver

#--------------------------------------------------------------------------
# Nova - Session Management Factory Kernel
#--------------------------------------------------------------------------
#
# @package  Nova
# @author   Nova Core Team
#
# This manager coordinates the creation and lifecycle resolution of session
# drivers. It uses configuration properties to instantiate custom key-value 
# state persistence layers across separate structural engine backends.
#

class SessionManager:

    def __init__(self, app: Any):
        """
        Create a new session manager instance.
        """
        self._app: Any = app
        self._custom_drivers: Dict[str, Any] = {}
        self._drivers: Dict[str, Any] = {}

    def driver(self, name: str = None) -> Any:
        """
        Resolve a specific session driver instance by name configuration identifier.
        """
        driver_name = name or config('session.driver', 'file')

        if driver_name not in self._drivers:
            self._drivers[driver_name] = self._create_driver(driver_name)

        return self._drivers[driver_name]

    def _create_driver(self, driver: str) -> Any:
        """
        Execute dynamic driver creation routes targeting specific engine drivers.
        """
        method = f"_create_{driver}_driver"
        
        if hasattr(self, method):
            return getattr(self, method)()
            
        raise ValueError(f"Unsupported session storage driver infrastructure: [{driver}].")

    def _create_file_driver(self) -> FileSessionDriver:
        """
        Instantiate the native filesystem storage serialization driver.
        """
        # Read the lifetime metric and scale out minutes configuration to raw seconds
        lifetime_seconds = int(config('session.lifetime', 120)) * 60
        
        # Resolve target framework disk pathways safely from the environment root
        storage_path = config('session.files', 'storage/framework/sessions')
        if not os.path.isabs(storage_path):
            storage_path = os.path.abspath(os.path.join(os.getcwd(), storage_path))

        return FileSessionDriver(storage_path, lifetime_seconds)

    def _create_database_driver(self) -> DatabaseSessionDriver:
        """
        Instantiate the standard relational database storage persistence engine.
        """
        lifetime_seconds = int(config('session.lifetime', 120)) * 60
        connection = self._app.make('db').connection()
        table = config('session.table', 'sessions')

        return DatabaseSessionDriver(connection, table, lifetime_seconds)

    def _create_array_driver(self) -> Any:
        """
        Instantiate a volatile local memory testing store (purged post-request).
        """
        class ArraySessionDriver:
            def __init__(self): self.storage = {}
            def read(self, session_id: str) -> dict: return self.storage.get(session_id, {})
            def write(self, session_id: str, data: dict) -> None: self.storage[session_id] = data
            def destroy(self, session_id: str) -> None: self.storage.pop(session_id, None)
            
        return ArraySessionDriver()