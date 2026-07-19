# engine/Support/helpers.py
from engine.Support.env import env

def base_url(path: str = '') -> str:
    """
    Automatically fetches the APP_URL from .env and appends the given path.
    Prevents double-slashes (e.g., http://localhost:8000//users).
    """
    url = env('APP_URL', 'http://localhost:8000').rstrip('/')
    
    if path:
        path = '/' + path.lstrip('/')
        
    return f"{url}{path}"

def asset(path: str) -> str:
    """
    Generates a full URL for CSS, JS, or image files in the public directory.
    Automatically prepends 'public/' if it isn't already included.
    """
    clean_path = path.lstrip('/')
    
    # Ensure we don't accidentally create '/public/public/css/style.css'
    if not clean_path.startswith('public/'):
        clean_path = f"public/{clean_path}"
        
    return base_url(clean_path)