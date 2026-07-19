# nova.py
import sys
import os

# Guarantee root paths map cleanly to execution context
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

# Boot application context and configurations
from engine.Support.env import load_env, env
load_env('.env')

# Import core consoles and migrators
from engine.Database.migration import Migrator
import engine.Console.commands as cmd

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("🌌 Nova CLI")
        print("Usage: python nova.py [command] [arguments]")
        print("\nCommands:")
        print("  serve                  Start the local development server")
        print("  make:controller <Name> Create a new controller class")
        print("  make:action <Name>     Create a single-responsibility action")
        print("  make:model <Name>      Create a new Nova-ORM active record model")
        print("  make:migration <Name>  Create a new database migration")
        print("  make:seeder <Name>     Create a new database seeder")
        print("  migrate                Run all pending migrations")
        print("  migrate:rollback       Rollback the last batch of migrations")
        print("  migrate:reset          Rollback ALL migrations")
        print("  migrate:refresh        Reset and re-run all migrations (use --seed to seed after)")
        print("  db:seed [Name]         Run database seeders (defaults to DatabaseSeeder)")
        sys.exit(0)

    command = sys.argv[1]
    
    # Validation helper for subcommands missing names
    def require_argument(error_message):
        if len(sys.argv) < 3:
            print(f"❌ {error_message}")
            sys.exit(1)
        return sys.argv[2]

    if command == 'serve':
        cmd.serve()
    elif command == 'make:controller':
        name = require_argument("Please provide a controller name.")
        cmd.make_controller(name)
    elif command == 'make:action':
        name = require_argument("Please provide an action name.")
        cmd.make_action(name)
    elif command == 'make:model':
        name = require_argument("Please provide a model name.")
        cmd.make_model(name)
    elif command == 'make:migration':
        name = require_argument("Please provide a migration name (e.g., create_users_table).")
        cmd.make_migration(name)
    elif command == 'make:seeder':
        name = require_argument("Please provide a seeder name.")
        cmd.make_seeder(name)
    elif command == 'migrate':
        Migrator().migrate()
    elif command == 'migrate:rollback':
        Migrator().rollback()
    elif command == 'migrate:reset':
        Migrator().reset()
    elif command == 'migrate:refresh':
        should_seed = '--seed' in sys.argv
        Migrator().refresh(seed=should_seed)
    elif command == 'db:seed':
        # Safely extract seeder name if provided, ignoring --flags
        seeder_name = "DatabaseSeeder"
        if len(sys.argv) > 2 and not sys.argv[2].startswith('--'):
            seeder_name = sys.argv[2]
        Migrator().seed(seeder_name)
    else:
        print(f"❌ Unknown command: {command}")