from typing import Callable, Any, Dict

class Container:
    def __init__(self):
        # Holds registered bindings (factories)
        self._bindings: Dict[str, Callable[['Container'], Any]] = {}
        # Holds shared instances (Singletons)
        self._instances: Dict[str, Any] = {}

    def bind(self, key: str, resolver: Callable[['Container'], Any]) -> None:
        """Register a binding with the container."""
        self._bindings[key] = resolver

    def singleton(self, key: str, resolver: Callable[['Container'], Any]) -> None:
        """Register a shared binding (Singleton) in the container."""
        def shared_resolver(container: 'Container') -> Any:
            if key not in self._instances:
                self._instances[key] = resolver(container)
            return self._instances[key]
        
        self.bind(key, shared_resolver)

    def make(self, key: str) -> Any:
        """Resolve the given type from the container."""
        if key not in self._bindings:
            raise Exception(f"No binding found for: {key}")
        
        # Execute the resolver function, passing the container itself
        return self._bindings[key](self)