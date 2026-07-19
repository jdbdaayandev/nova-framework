# engine/Database/seeder.py
import importlib

class Seeder:
    def call(self, seeder_names: list):
        """Allows a seeder to execute an array of other seeders sequentially."""
        for name in seeder_names:
            print(f"🌱 Running Seeder: {name}")
            try:
                # Dynamically import the seeder class from the database.seeders module
                module = importlib.import_module(f"database.seeders.{name}")
                seeder_class = getattr(module, name)
                
                # Instantiate and run
                seeder_instance = seeder_class()
                seeder_instance.run()
            except ModuleNotFoundError:
                print(f"❌ Error: Seeder '{name}' not found.")
            except AttributeError:
                print(f"❌ Error: Class '{name}' not found inside its module.")
            except Exception as e:
                print(f"❌ Execution Error in {name}: {e}")

    def run(self):
        """The main execution block for the seeder. Override this in child classes."""
        pass