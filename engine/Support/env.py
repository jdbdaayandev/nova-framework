import os
import re

def load_env(file_path='.env'):
    """
    Parses a .env file and loads the variables into os.environ.
    Zero-dependency implementation with nested variable interpolation.
    """
    if not os.path.exists(file_path):
        print(f"⚠️ Warning: No {file_path} file found. Relying on system environment variables.")
        return

    raw_values = {}

    with open(file_path, 'r') as file:
        for line in file:
            line = line.strip()
            
            # Ignore empty lines and comments
            if not line or line.startswith('#'):
                continue

            # Split only on the first '=' in case the value contains '='
            if '=' in line:
                key, value = line.split('=', 1)
                key = key.strip()
                value = value.strip()

                # Strip out inline comments if they exist outside of strings
                if ' #' in value and not (value.startswith('"') or value.startswith("'")):
                    value = value.split(' #', 1)[0].strip()

                # Remove surrounding quotes if the user added them
                if (value.startswith('"') and value.endswith('"')) or \
                   (value.startswith("'") and value.endswith("'")):
                    value = value[1:-1]

                raw_values[key] = value

    # Interpolate nested variables like ${APP_NAME} (resolves up to 3 nested layers deep)
    for _ in range(3):
        has_changed = False
        for key, value in raw_values.items():
            matches = re.findall(r'\$\{([^}]+)\}', value)
            for match in matches:
                # Find the target in our file config map or fallback to existing system env variables
                target_val = raw_values.get(match, os.environ.get(match, ''))
                value = value.replace(f"${{{match}}}", target_val)
                raw_values[key] = value
                has_changed = True
        if not has_changed:
            break

    # Commit parsed configuration items to system environment
    for key, value in raw_values.items():
        os.environ[key] = value

def env(key: str, default=None):
    """
    Helper function to safely retrieve an environment variable.
    Automatically parses strings like 'true', 'false', and 'null' into Python equivalents.
    """
    value = os.environ.get(key, default)
    
    if isinstance(value, str):
        lower_value = value.lower()
        if lower_value == 'true':
            return True
        if lower_value == 'false':
            return False
        if lower_value in ('null', 'none', ''):
            return None
            
    return value