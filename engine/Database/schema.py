# engine/Database/schema.py
from engine.Database.connection import DB
from engine.Support.env import env

class Column:
    def __init__(self, name: str, type_str: str):
        self.name = name
        self.type_str = type_str
        self.is_nullable = False
        self.is_unique = False
        self.default_val = None

    def nullable(self):
        self.is_nullable = True
        return self

    def unique(self):
        self.is_unique = True
        return self

    def default(self, value):
        self.default_val = value
        return self

    def compile(self) -> str:
        if "PRIMARY KEY" in self.type_str:
            return f"{self.name} {self.type_str}"
            
        parts = [self.name, self.type_str]
        if self.is_unique:
            parts.append("UNIQUE")
        if not self.is_nullable:
            parts.append("NOT NULL")
        if self.default_val is not None:
            if isinstance(self.default_val, str):
                parts.append(f"DEFAULT '{self.default_val}'")
            elif isinstance(self.default_val, bool):
                parts.append(f"DEFAULT {int(self.default_val)}")
            else:
                parts.append(f"DEFAULT {self.default_val}")
                
        return " ".join(parts)


class ForeignKey:
    def __init__(self, column_name: str):
        self.column_name = column_name
        self.ref_table = None
        self.ref_column = 'id'
        self.on_delete_action = None
        self.on_update_action = None

    def references(self, column: str):
        self.ref_column = column
        return self

    def on(self, table: str):
        self.ref_table = table
        return self
        
    def constrained(self, table: str = None):
        """Shortcut: derives table name from column if none provided (e.g., user_id -> users)."""
        if not table:
            # simple pluralization: user_id -> users
            table = self.column_name.replace('_id', '') + 's'
        self.ref_table = table
        return self

    def onDelete(self, action: str):
        """e.g., 'cascade', 'set null', 'restrict'"""
        self.on_delete_action = action.upper()
        return self

    def onUpdate(self, action: str):
        self.on_update_action = action.upper()
        return self

    def compile(self) -> str:
        if not self.ref_table:
            raise ValueError(f"Foreign key for '{self.column_name}' is missing a referenced table.")
        
        sql = f"FOREIGN KEY ({self.column_name}) REFERENCES {self.ref_table}({self.ref_column})"
        if self.on_delete_action:
            sql += f" ON DELETE {self.on_delete_action}"
        if self.on_update_action:
            sql += f" ON UPDATE {self.on_update_action}"
        return sql


class Blueprint:
    def __init__(self, table_name: str):
        self.table_name = table_name
        self.columns = []
        self.foreign_keys = []

    def id(self, name: str = 'id'):
        driver = env('DB_CONNECTION', 'sqlite').lower()
        if driver == 'sqlite':
            col_type = "INTEGER PRIMARY KEY AUTOINCREMENT"
        elif driver == 'mysql':
            col_type = "INT AUTO_INCREMENT PRIMARY KEY"
        else:
            col_type = "SERIAL PRIMARY KEY"
        col = Column(name, col_type)
        self.columns.append(col)
        return col

    def string(self, name: str, length: int = 255):
        col = Column(name, f"VARCHAR({length})")
        self.columns.append(col)
        return col

    def text(self, name: str):
        col = Column(name, "TEXT")
        self.columns.append(col)
        return col

    def integer(self, name: str):
        col = Column(name, "INTEGER")
        self.columns.append(col)
        return col

    def float(self, name: str):
        col = Column(name, "FLOAT")
        self.columns.append(col)
        return col

    def boolean(self, name: str):
        col = Column(name, "BOOLEAN")
        self.columns.append(col)
        return col
        
    def date(self, name: str):
        col = Column(name, "DATE")
        self.columns.append(col)
        return col
        
    def datetime(self, name: str):
        col = Column(name, "DATETIME")
        self.columns.append(col)
        return col

    def json(self, name: str):
        col = Column(name, "JSON")
        self.columns.append(col)
        return col

    def timestamps(self):
        self.columns.append(Column("created_at", "TIMESTAMP DEFAULT CURRENT_TIMESTAMP"))
        self.columns.append(Column("updated_at", "TIMESTAMP DEFAULT CURRENT_TIMESTAMP"))

    def foreign(self, column_name: str) -> ForeignKey:
        """Define a foreign key constraint on an existing column."""
        fk = ForeignKey(column_name)
        self.foreign_keys.append(fk)
        return fk

    def foreignId(self, name: str) -> ForeignKey:
        """Shortcut: Creates an integer column and returns a ForeignKey builder."""
        self.integer(name)
        return self.foreign(name)


class SchemaContext:
    def __init__(self, table_name: str):
        self.blueprint = Blueprint(table_name)

    def __enter__(self):
        return self.blueprint

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            return False
            
        col_definitions = [col.compile() for col in self.blueprint.columns]
        fk_definitions = [fk.compile() for fk in self.blueprint.foreign_keys]
        
        # Combine columns and constraints
        all_definitions = col_definitions + fk_definitions
        
        sql = f"CREATE TABLE IF NOT EXISTS {self.blueprint.table_name} (\n    "
        sql += ",\n    ".join(all_definitions)
        sql += "\n)"
        
        DB.query(sql)


class Schema:
    @staticmethod
    def create(table_name: str) -> SchemaContext:
        return SchemaContext(table_name)

    @staticmethod
    def drop_if_exists(table_name: str):
        DB.query(f"DROP TABLE IF EXISTS {table_name}")