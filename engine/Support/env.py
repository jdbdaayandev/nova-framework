# engine/Support/env.py
import os

def load_env(file_path='.env'):
    """
    Parses a .env file and loads the variables into os.environ.
    """
    if not os.path.exists(file_path):
        return

    with open(file_path, 'r') as f:
        for line in f:
            line = line.strip()
            
            # Ignore empty lines and comments
            if not line or line.startswith('#'):
                continue
            
            # Split only on the first '=' character
            if '=' in line:
                key, value = line.split('=', 1)
                key = key.strip()
                value = value.strip()
                
                # Strip wrapping single or double quotes if present
                if value.startswith(("'", '"')) and value.endswith(("'", '"')):
                    value = value[1:-1]
                    
                # Inject into environment if not already set by the OS
                if key not in os.environ:
                    os.environ[key] = value

def env(key, default=None):
    """
    Helper to get an environment variable with an optional default.
    """
    return os.environ.get(key, default)