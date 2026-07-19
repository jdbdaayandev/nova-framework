# nova.py
import sys
import os
from wsgiref.simple_server import make_server

# Ensure the framework root is in Python's environment path for clean imports
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

def create_file(path: str, content: str):
    """Helper to safely create files and their directories."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    if os.path.exists(path):
        print(f"❌ Error: {path} already exists.")
        sys.exit(1)
        
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"✨ Created: {path}")

def make_controller(name: str):
    """Scaffolds a new Controller class."""
    if not name.endswith('Controller'):
        name += 'Controller'
    content = f"""from engine.Http.request import Request
from engine.Http.response import Response

class {name}:
    def index(self, request: Request) -> Response:
        return Response("Welcome to the {name} index!")
"""
    create_file(f"app/Http/Controllers/{name}.py", content)

def make_action(name: str):
    """Scaffolds a new Action class."""
    if not name.endswith('Action'):
        name += 'Action'
    content = f"""class {name}:
    def execute(self, data: dict):
        \"\"\"Execute the business logic for {name}.\"\"\"
        pass
"""
    create_file(f"app/Actions/{name}.py", content)

def serve():
    """Starts the local development server by hosting the Front Controller."""
    print("🌌 Starting Nova development server...")
    
    try:
        # Reach into the public front controller to grab the WSGI app definition
        from public.index import application
    except ImportError as e:
        print(f"❌ Framework Boot Error: Could not locate public/index.py\n{e}")
        sys.exit(1)

    host = '127.0.0.1'
    port = 8000
    print(f"🚀 Framework booted. Listening on http://{host}:{port}...")
    
    # Keep-Alive Loop lives strictly inside the CLI wrapper
    try:
        server = make_server(host, port, application)
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Nova server stopped gracefully.")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("🌌 Nova CLI")
        print("Usage: python nova.py [command] [arguments]")
        print("\nCommands:")
        print("  serve                   Start the local development server")
        print("  make:controller <Name>  Create a new controller class")
        print("  make:action <Name>      Create a single-responsibility action")
        sys.exit(0)

    command = sys.argv[1]
    
    if command == 'serve':
        serve()
    elif command == 'make:controller':
        if len(sys.argv) < 3:
            print("❌ Please provide a controller name.")
            sys.exit(1)
        make_controller(sys.argv[2])
    elif command == 'make:action':
        if len(sys.argv) < 3:
            print("❌ Please provide an action name.")
            sys.exit(1)
        make_action(sys.argv[2])
    else:
        print(f"❌ Unknown command: {command}")