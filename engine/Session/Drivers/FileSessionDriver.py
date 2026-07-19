import os
import pickle
from typing import Dict, Any

#--------------------------------------------------------------------------
# Nova - File-Based Session Storage Driver
#--------------------------------------------------------------------------
#
# @package  Nova
# @author   Nova Core Team
#
# This component serializes and reads raw dictionary structures targeting
# isolated server asset paths. It functions with zero foreign library lookups.
#

class FileSessionDriver:

    def __init__(self, path: str, lifetime: int):
        """
        Initialize the file-backed persistence engine instance.
        """
        self._path: str = path
        self._lifetime: int = lifetime
        
        # Ensure target server storage folders exist out-of-the-box
        if not os.path.exists(path):
            os.makedirs(path, exist_ok=True)

    def read(self, session_id: str) -> Dict[str, Any]:
        """
        Extract and deserialize runtime attributes from file targets.
        """
        target_file = os.path.join(self._path, session_id)

        if not os.path.isfile(target_file):
            return {}

        # Validate structural expiry metrics before loading
        if (os.path.getmtime(target_file) + self._lifetime) < os.time():
            self.destroy(session_id)
            return {}

        try:
            with open(target_file, 'rb') as storage_node:
                return pickle.load(storage_node)
        except (IOError, pickle.PickleError):
            return {}

    def write(self, session_id: str, data: Dict[str, Any]) -> None:
        """
        Serialize application attributes down into physical storage block addresses.
        """
        target_file = os.path.join(self._path, session_id)
        
        try:
            with open(target_file, 'wb') as storage_node:
                pickle.dump(data, storage_node, protocol=pickle.HIGHEST_PROTOCOL)
        except IOError:
            pass

    def destroy(self, session_id: str) -> None:
        """
        Purge the corresponding data file out of active server nodes.
        """
        target_file = os.path.join(self._path, session_id)
        if os.path.isfile(target_file):
            try:
                os.remove(target_file)
            except OSError:
                pass