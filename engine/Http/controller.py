from typing import Any, Dict, List, Optional

class Controller:
    """
    The Foundation Engine Controller.
    
    All application controllers extend this class to register controller-level
    middleware pipelines and manage targeted filter configurations.
    """

    def __init__(self) -> None:
        # Array tracking assigned local middleware layers and conditional constraints
        self._middleware_stack: List[Dict[str, Any]] = []

    def middleware(
        self, 
        middleware_name: str, 
        only: Optional[List[str]] = None, 
        except_methods: Optional[List[str]] = None
    ) -> None:
        """
        Register a middleware layer directly inside the controller constructor.
        """
        self._middleware_stack.append({
            'name': middleware_name,
            'only': only or [],
            'except': except_methods or []
        })

    def get_middleware_for_method(self, method_name: str) -> List[str]:
        """
        Evaluates the controller stack rules and filters active middleware hooks.
        """
        active_middleware: List[str] = []
        
        for layer in self._middleware_stack:
            only_rules = layer['only']
            except_rules = layer['except']
            
            if only_rules and method_name not in only_rules:
                continue
            if except_rules and method_name in except_rules:
                continue
                
            active_middleware.append(layer['name'])
            
        return active_middleware