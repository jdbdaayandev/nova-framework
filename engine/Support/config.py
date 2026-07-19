import os
import importlib.util

class ConfigRepository:
    _items = {}

    @classmethod
    def load_from_directory(cls, config_dir):
        """Scans the config directory and dynamically imports valid configuration modules."""
        cls._items = {}
        if not os.path.exists(config_dir):
            return

        for filename in os.listdir(config_dir):
            if filename.endswith('.py'):
                module_name = filename[:-3]  # Strip '.py' extension
                filepath = os.path.join(config_dir, filename)
                
                # Use standard library utilities to import and evaluate the module natively
                spec = importlib.util.spec_from_file_location(module_name, filepath)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                # Safely extract the CONFIG dictionary array from the module namespace
                cls._items[module_name] = getattr(module, 'CONFIG', {})

    @classmethod
    def get(cls, key, default=None):
        """Resolves deep configuration keys using dot notation."""
        parts = key.split('.')
        segment = cls._items
        
        for part in parts:
            if isinstance(segment, dict) and part in segment:
                segment = segment[part]
            else:
                return default
        return segment

def config(key, default=None):
    """Global configuration helper gateway."""
    return ConfigRepository.get(key, default)