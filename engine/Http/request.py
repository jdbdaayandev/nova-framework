import urllib.parse
from typing import Dict, Any

class Request:
    def __init__(self, environ: Dict[str, Any]):
        self.environ = environ
        self.method = environ.get('REQUEST_METHOD', 'GET').upper()
        self.path = environ.get('PATH_INFO', '/')
        
        # Parse query string into a dictionary (e.g., ?search=python)
        query_string = environ.get('QUERY_STRING', '')
        self.query = urllib.parse.parse_qs(query_string)
        
        # Parse WSGI headers (they start with HTTP_)
        self.headers = {}
        for key, value in environ.items():
            if key.startswith('HTTP_'):
                # Convert HTTP_USER_AGENT to User-Agent
                header_name = key[5:].replace('_', '-').title()
                self.headers[header_name] = value
            elif key in ('CONTENT_TYPE', 'CONTENT_LENGTH'):
                header_name = key.replace('_', '-').title()
                self.headers[header_name] = value

    def input(self, key: str, default: Any = None) -> Any:
        """Helper to get a query parameter value."""
        if key in self.query:
            # parse_qs returns lists, so we return the first item
            return self.query[key][0]
        return default