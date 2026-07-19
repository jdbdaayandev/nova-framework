# engine/Console/commands.py
import os
import sys
from datetime import datetime
from wsgiref.simple_server import make_server
from engine.Support.env import env

def create_file(path: str, content: str):
    """Helper to safely create directories and write files if they don't exist."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    if os.path.exists(path):
        print(f"❌ Error: {path} already exists.")
        sys.exit(1)
        
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"✨ Created: {path}")

def make_controller(name: str):
    """Scaffolds a new controller class."""
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
    """Scaffolds a single-responsibility action class."""
    if not name.endswith('Action'):
        name += 'Action'
    content = f"""class {name}:
    def execute(self, data: dict):
        \"\"\"Execute the business logic for {name}.\"\"\"
        pass
"""
    create_file(f"app/Actions/{name}.py", content)

def make_model(name: str):
    """Scaffolds an Active Record model class."""
    name = name.strip().capitalize()
    content = f"""from engine.Database.model import Model

class {name}(Model):
    # By default, Nova-ORM assumes your table is the plural lowercase name of the model.
    # To override this, uncomment the line below:
    # __table__ = '{name.lower()}s'
    pass
"""
    create_file(f"app/Models/{name}.py", content)

def make_migration(name: str):
    """Scaffolds a clean Schema blueprint migration file with helpful usage docs."""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"{timestamp}_{name.lower()}.py"
    
    table_name = name.lower()
    if name.startswith('create_') and name.endswith('_table'):
        table_name = name[7:-6]
        
    content = f"""# ==============================================================================
# Nova Migration Blueprint Reference
# ==============================================================================
# Column Types:
#   table.string('name')     table.text('name')        table.integer('name')
#   table.float('name')      table.boolean('name')     table.json('name')
#   table.date('name')       table.datetime('name')
#
# Modifiers:
#   .nullable() | .unique() | .default(value)
#
# Foreign Keys:
#   table.foreignId('user_id').constrained().onDelete('cascade')
#   table.foreign('custom_id').references('id').on('roles').onUpdate('restrict')
# ==============================================================================

from engine.Database.schema import Schema

class Migration:
    def up(self):
        with Schema.create('{table_name}') as table:
            table.id()
            # Add your custom fields here
            table.timestamps()

    def down(self):
        Schema.drop_if_exists('{table_name}')
"""
    create_file(f"database/migrations/{filename}", content)

def make_seeder(name: str):
    """Scaffolds a clean, ORM-driven database seeder class."""
    if not name.endswith('Seeder'):
        name += 'Seeder'
        
    content = f"""from engine.Database.seeder import Seeder
# from app.Models.User import User  # Import your ORM Models here

class {name}(Seeder):
    def run(self):
        # Example 1: Creating records via Nova-ORM
        # User.create({{
        #     'name': 'Admin User',
        #     'email': 'admin@nova.dev',
        # }})
        
        # Example 2: Calling other seeders (useful for the main DatabaseSeeder)
        # self.call(['RoleSeeder', 'PermissionSeeder'])
        pass
"""
    create_file(f"database/seeders/{name}.py", content)

def serve():
    """Starts the local development application server."""
    print("🌌 Starting Nova development server...")
    
    try:
        from public.index import application
    except ImportError as e:
        print(f"❌ Framework Boot Error: Could not locate public/index.py\n{e}")
        sys.exit(1)

    host = env('APP_HOST', '127.0.0.1')
    port = int(env('APP_PORT', 8000))
    
    print(f"🚀 Framework booted. Listening on http://{host}:{port}...")
    
    try:
        server = make_server(host, port, application)
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Nova server stopped gracefully.")