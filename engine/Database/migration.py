# engine/Database/migration.py
import os
import sys
import importlib
import importlib.util
from engine.Database.connection import DB

class Migrator:
    def __init__(self):
        self.migrations_dir = os.path.join(os.getcwd(), 'database', 'migrations')
        self._ensure_migrations_table()

    def _ensure_migrations_table(self):
        """Creates the tracking table if it doesn't exist. Omitted ID to avoid cross-database auto-increment syntax issues."""
        DB.query("""
            CREATE TABLE IF NOT EXISTS migrations (
                migration VARCHAR(255),
                batch INTEGER
            )
        """)

    def _get_ran_migrations(self):
        """Fetches a list of migration filenames that have already been executed."""
        results = DB.query("SELECT migration FROM migrations")
        # Handle different driver return formats (list of dicts vs list of tuples)
        if not results:
            return []
        if isinstance(results[0], dict):
            return [row['migration'] for row in results]
        return [row[0] for row in results]

    def _get_migration_files(self):
        """Returns a chronologically sorted list of migration python files."""
        if not os.path.exists(self.migrations_dir):
            return []
        files = [f for f in os.listdir(self.migrations_dir) if f.endswith('.py') and f != '__init__.py']
        return sorted(files)

    def _load_module(self, file_name):
        """Dynamically loads a python file as a module. Required because timestamped files can't be imported via standard importlib."""
        file_path = os.path.join(self.migrations_dir, file_name)
        module_name = file_name.replace('.py', '')
        spec = importlib.util.spec_from_file_location(module_name, file_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def migrate(self):
        """Executes all pending migrations."""
        ran_migrations = self._get_ran_migrations()
        all_files = self._get_migration_files()
        
        pending = [f for f in all_files if f not in ran_migrations]

        if not pending:
            print("✨ Nothing to migrate. Database is up to date.")
            return

        # Determine the next batch number
        batch_result = DB.query("SELECT MAX(batch) as max_batch FROM migrations")
        if not batch_result:
            next_batch = 1
        elif isinstance(batch_result[0], dict):
            next_batch = (batch_result[0]['max_batch'] or 0) + 1
        else:
            next_batch = (batch_result[0][0] or 0) + 1

        print(f"🚀 Running batch {next_batch}...")

        for file_name in pending:
            print(f"Migrating: {file_name}")
            module = self._load_module(file_name)
            
            # Instantiate the Migration class and run up()
            migration = module.Migration()
            migration.up()
            
            # Record it in the tracking table
            DB.query("INSERT INTO migrations (migration, batch) VALUES (?, ?)", (file_name, next_batch))
            print(f"✅ Migrated: {file_name}")

    def rollback(self):
        """Rolls back the most recent batch of migrations."""
        # Find the latest batch
        batch_result = DB.query("SELECT MAX(batch) as max_batch FROM migrations")
        
        latest_batch = None
        if batch_result:
            if isinstance(batch_result[0], dict):
                latest_batch = batch_result[0]['max_batch']
            else:
                latest_batch = batch_result[0][0]

        if not latest_batch:
            print("✨ No migrations to rollback.")
            return

        print(f"⏪ Rolling back batch {latest_batch}...")

        # Fetch migrations belonging to the latest batch
        migrations_to_rollback = DB.query("SELECT migration FROM migrations WHERE batch = ? ORDER BY migration DESC", (latest_batch,))
        
        if not migrations_to_rollback:
            return

        # Handle different return formats
        if isinstance(migrations_to_rollback[0], dict):
            files = [row['migration'] for row in migrations_to_rollback]
        else:
            files = [row[0] for row in migrations_to_rollback]

        for file_name in files:
            print(f"Rolling back: {file_name}")
            module = self._load_module(file_name)
            
            # Instantiate the Migration class and run down()
            migration = module.Migration()
            migration.down()
            
            # Remove from tracking table
            DB.query("DELETE FROM migrations WHERE migration = ?", (file_name,))
            print(f"✅ Rolled back: {file_name}")
            
    def reset(self):
        """Rolls back ALL migrations."""
        results = DB.query("SELECT migration FROM migrations ORDER BY migration DESC")
        
        if not results:
            print("✨ No migrations to reset.")
            return

        # Handle different driver return formats
        if isinstance(results[0], dict):
            files = [row['migration'] for row in results]
        else:
            files = [row[0] for row in results]

        print("⏪ Resetting all migrations...")
        for file_name in files:
            print(f"Rolling back: {file_name}")
            module = self._load_module(file_name)
            
            migration = module.Migration()
            migration.down()
            
            DB.query("DELETE FROM migrations WHERE migration = ?", (file_name,))
            print(f"✅ Rolled back: {file_name}")

    def refresh(self, seed: bool = False):
        """Rolls back all migrations and runs them again."""
        print("🔄 Refreshing database...")
        self.reset()
        self.migrate()
        
        if seed:
            self.seed()

    def seed(self, seeder_name: str = "DatabaseSeeder"):
        """Locates and executes the specified database seeder."""
        print(f"🌱 Starting database seeding ({seeder_name})...")
        try:
            # Seeders don't have numbers at the front, so standard importlib works fine here
            module = importlib.import_module(f"database.seeders.{seeder_name}")
            seeder_class = getattr(module, seeder_name)
            
            seeder_instance = seeder_class()
            seeder_instance.run()
            
            print(f"✅ Database seeding completed successfully.")
        except ModuleNotFoundError:
            print(f"❌ Cannot find seeder file: database/seeders/{seeder_name}.py")
        except AttributeError:
            print(f"❌ The file exists, but class '{seeder_name}' is missing inside it.")
        except Exception as e:
            print(f"❌ Error during seeding: {e}")