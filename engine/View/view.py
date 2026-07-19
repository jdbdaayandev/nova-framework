# engine/View/view.py
import os
import re
from engine.Http.response import Response
from engine.Support.helpers import asset  # <-- Import the asset helper

def view(template_name: str, data: dict = None) -> Response:
    """
    Renders an HTML template using pure Python (Zero Dependencies).
    Supports {{ variable }} syntax and {{ asset('path') }} function calls.
    """
    if data is None:
        data = {}

    # Locate the resources/views directory
    # Moves up from engine/View/view.py to project root, then into resources/views
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    template_path = os.path.join(base_dir, 'resources', 'views', f"{template_name}.html")

    if not os.path.exists(template_path):
        return Response(f"Template [{template_name}.html] not found in resources/views/", status=404)

    # Read the native HTML file
    with open(template_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Parse asset() helper functions specifically
    def evaluate_asset(match):
        path = match.group(1)
        return asset(path)

    # Matches {{ asset('path') }} or {{ asset("path") }}
    content = re.sub(r'\{\{\s*asset\([\'"]([^\'"]+)[\'"]\)\s*\}\}', evaluate_asset, content)

    # 2. Regex function to find and replace {{ variable }} with actual data
    def replace_placeholder(match):
        variable_name = match.group(1).strip()
        # Returns the value if found, otherwise leaves it empty
        return str(data.get(variable_name, ''))

    # Replace all occurrences of {{ variable }}
    rendered_content = re.sub(r'\{\{\s*([a-zA-Z0-9_]+)\s*\}\}', replace_placeholder, content)

    # Return a clean HTTP Response with HTML headers
    return Response(rendered_content, headers=[('Content-Type', 'text/html')])