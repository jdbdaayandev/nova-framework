import json
import time
from typing import Any, Dict, Optional

#--------------------------------------------------------------------------
# Nova - Database-Backed Session Storage Driver
#--------------------------------------------------------------------------
#
# @package  Nova
# @author   Nova Core Team
#
# This component acts as the translation tier between the Session Kernel
# engine and standard relational database structures. It abstracts raw state 
# values into JSON blocks for cross-platform data alignment.
#

class DatabaseSessionDriver:

    def __init__(self, connection: Any, table: str, lifetime: int):
        """
        Initialize the database-backed session driver instance.
        """
        self._connection: Any = connection
        self._table: str = table
        self._lifetime: int = lifetime
        self._placeholder: str = self._determine_param_style()

    #--------------------------------------------------------------------------
    # Driver Interface Contract Implementation
    #--------------------------------------------------------------------------

    def read(self, session_id: str) -> Dict[str, Any]:
        """
        Retrieve and decode session attributes from the database cluster.
        """
        cursor = self._connection.cursor()
        query = f"SELECT payload, last_activity FROM {self._table} WHERE id = {self._placeholder}"
        
        try:
            cursor.execute(query, (session_id,))
            row = cursor.fetchone()
            
            if not row:
                return {}

            payload, last_activity = row

            # If the session has drifted past the lifetime threshold, purge it
            if (last_activity + self._lifetime) < int(time.time()):
                self.destroy(session_id)
                return {}

            return json.loads(payload)
            
        except Exception:
            return {}
        finally:
            cursor.close()

    def write(self, session_id: str, data: Dict[str, Any]) -> None:
        """
        Commit the active application state attributes back to the session layout.
        """
        cursor = self._connection.cursor()
        payload = json.dumps(data)
        current_time = int(time.time())

        try:
            # Check for existing record row coordinates to split between INSERT and UPDATE paths
            lookup_query = f"SELECT 1 FROM {self._table} WHERE id = {self._placeholder}"
            cursor.execute(lookup_query, (session_id,))
            exists = cursor.fetchone()

            if exists:
                update_query = (
                    f"UPDATE {self._table} SET payload = {self._placeholder}, "
                    f"last_activity = {self._placeholder} WHERE id = {self._placeholder}"
                )
                cursor.execute(update_query, (payload, current_time, session_id))
            else:
                insert_query = (
                    f"INSERT INTO {self._table} (id, payload, last_activity) "
                    f"VALUES ({self._placeholder}, {self._placeholder}, {self._placeholder})"
                )
                cursor.execute(insert_query, (session_id, payload, current_time))
                
            self._connection.commit()
            
        except Exception:
            self._connection.rollback()
            raise
        finally:
            cursor.close()

    def destroy(self, session_id: str) -> None:
        """
        Purge an explicit session identity boundary out of the database cluster.
        """
        cursor = self._connection.cursor()
        query = f"DELETE FROM {self._table} WHERE id = {self._placeholder}"
        
        try:
            cursor.execute(query, (session_id,))
            self._connection.commit()
        except Exception:
            self._connection.rollback()
        finally:
            cursor.close()

    def gc(self) -> None:
        """
        Garbage collect records that have exceeded their designated expiration age.
        """
        cursor = self._connection.cursor()
        cutoff = int(time.time()) - self._lifetime
        query = f"DELETE FROM {self._table} WHERE last_activity < {self._placeholder}"
        
        try:
            cursor.execute(query, (cutoff,))
            self._connection.commit()
        except Exception:
            self._connection.rollback()
        finally:
            cursor.close()

    #--------------------------------------------------------------------------
    # Architectural Internal Support Methods
    #--------------------------------------------------------------------------

    def _determine_param_style(self) -> str:
        """
        Infer the driver binding style pattern by assessing engine signatures.
        """
        module_signature = type(self._connection).__module__.lower()
        
        if 'sqlite' in module_signature:
            return '?'
            
        # Matches common PostgreSQL (psycopg2) and MySQL engines
        return '%s'