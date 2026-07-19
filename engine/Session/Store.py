import secrets
import time
from typing import Any, Dict, Optional

#--------------------------------------------------------------------------
# Nova - Session Component Store
#--------------------------------------------------------------------------
#
# @package  Nova
# @author   Nova Core Team
#
# The Session Store represents the internal data payload container for the 
# current request execution lifecycle. It manages session state values, 
# flash notification arrays, and unique cryptographic session markers.
#

class Store:
    
    def __init__(self, name: str, driver: Any, session_id: Optional[str] = None):
        """
        Create a new session store instance.
        """
        self._name: str = name
        self._driver: Any = driver
        self._id: str = session_id if session_id else self._generate_session_id()
        self._attributes: Dict[str, Any] = {}
        
        # Start the request cycle with empty flash data structures
        self._attributes['_flash'] = {
            'old': [],
            'new': []
        }
        
        # Hydrate internal memory from the configured persistent driver
        self.start()

    #--------------------------------------------------------------------------
    # Lifecycle Management Operations
    #--------------------------------------------------------------------------

    def start(self) -> None:
        """
        Load the session data payload from the designated engine storage driver.
        """
        data = self._driver.read(self._id)
        
        if data and isinstance(data, dict):
            self._attributes = data
            
            # Age existing flash arrays: data from last request moves to 'old'
            if '_flash' in self._attributes:
                self._attributes['_flash']['old'] = self._attributes['_flash'].get('new', [])
                self._attributes['_flash']['new'] = []
        else:
            self._attributes = {
                '_flash': {'old': [], 'new': []}
            }

    def save(self) -> None:
        """
        Commit the active state layout array back into the storage driver.
        """
        # Clean out stale flash items before long-term serialization
        if '_flash' in self._attributes:
            for old_key in self._attributes['_flash'].get('old', []):
                if old_key not in self._attributes['_flash'].get('new', []):
                    self._attributes.pop(old_key, None)
            
            # Rotate target frames
            self._attributes['_flash']['old'] = []
            
        self._driver.write(self._id, self._attributes)

    #--------------------------------------------------------------------------
    # Key-Value Attribute Operations
    #--------------------------------------------------------------------------

    def get(self, key: str, default: Any = None) -> Any:
        """
        Retrieve an item from the session attributes dictionary structure.
        """
        return self._attributes.get(key, default)

    def put(self, key: str, value: Any) -> None:
        """
        Assign an item or list configuration payload directly to the session array.
        """
        self._attributes[key] = value

    def has(self, key: str) -> bool:
        """
        Determine if the given structural key is initialized inside the session.
        """
        return key in self._attributes

    def forget(self, key: str) -> None:
        """
        Remove an explicit payload attribute coordinate out of memory.
        """
        self._attributes.pop(key, None)

    def flush(self) -> None:
        """
        Completely clear out the active runtime session attributes payload map.
        """
        self._attributes = {
            '_flash': {'old': [], 'new': []}
        }

    #--------------------------------------------------------------------------
    # Flash Sub-System Pipeline Architecture
    #--------------------------------------------------------------------------

    def flash(self, key: str, value: Any) -> None:
        """
        Flash a variable payload key to survive exactly one subsequent request cycle.
        """
        self.put(key, value)
        
        if '_flash' not in self._attributes:
            self._attributes['_flash'] = {'old': [], 'new': []}
            
        if key not in self._attributes['_flash']['new']:
            self._attributes['_flash']['new'].append(key)

    def reflash(self) -> None:
        """
        Retain all present temporary structural flash data across another execution hop.
        """
        if '_flash' in self._attributes:
            self._attributes['_flash']['new'].extend(self._attributes['_flash'].get('old', []))
            self._attributes['_flash']['old'] = []

    #--------------------------------------------------------------------------
    # Engine Internal Cryptography Operations
    #--------------------------------------------------------------------------

    def id(self) -> str:
        """
        Get the current underlying unique identifier string token.
        """
        return self._id

    def _generate_session_id(self) -> str:
        """
        Generate a cryptographically secure alpha-numeric unique string token.
        """
        return secrets.token_urlsafe(32)