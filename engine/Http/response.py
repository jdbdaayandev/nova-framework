# engine/Http/response.py
from http import HTTPStatus
from typing import Dict, Any, Union, List, Tuple

class Response:
    def __init__(
        self, 
        content: str = '', 
        status: int = 200, 
        headers: Union[Dict[str, str], List[Tuple[str, str]]] = None
    ):
        self.content = content
        self.status = status
        
        # FIX: If a list of tuples is passed, safely normalize it into a dictionary
        if isinstance(headers, list):
            self.headers = dict(headers)
        else:
            self.headers = headers or {'Content-Type': 'text/html; charset=utf-8'}

    @property
    def status_string(self) -> str:
        """Converts integer 200 to string '200 OK' for WSGI."""
        try:
            status_phrase = HTTPStatus(self.status).phrase
            return f"{self.status} {status_phrase}"
        except ValueError:
            return f"{self.status} Unknown"