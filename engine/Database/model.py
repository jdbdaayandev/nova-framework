from datetime import datetime
from typing import List, Optional, Any
from engine.Database.connection import DB
from engine.Support.config import config

class Model:
    """
    Nova-ORM Base Model
    Implements Active Record pattern for database-agnostic interactions.
    """
    __table__: Optional[str] = None
    __primary_key__: str = 'id'
    
    # Laravel Style Feature: Automatically manage created_at and updated_at fields
    has_timestamps: bool = True

    def __init__(self, **kwargs):
        super().__setattr__('_attributes', kwargs)

    def __getattr__(self, key: str) -> Any:
        if key in self._attributes:
            return self._attributes[key]
        raise AttributeError(f"'{self.__class__.__name__}' model has no attribute '{key}'")

    def __setattr__(self, key: str, value: Any):
        if key.startswith('_') or key in ['__table__', '__primary_key__', 'has_timestamps']:
            super().__setattr__(key, value)
        else:
            self._attributes[key] = value

    @classmethod
    def _placeholder(cls) -> str:
        """
        Dynamically resolves the proper SQL binding placeholder based on the active configuration.
        SQLite uses '?', while MySQL/PostgreSQL drivers use '%s'.
        """
        active_connection = config('database.default', 'sqlite')
        driver = config(f'database.connections.{active_connection}.driver', 'sqlite')
        
        return '%s' if driver in ['mysql', 'postgresql'] else '?'

    @classmethod
    def get_table(cls) -> str:
        """Resolves the table name. Defaults to lowercase class name + 's'."""
        return cls.__table__ or f"{cls.__name__.lower()}s"

    @classmethod
    def all(cls) -> List['Model']:
        """Fetches all records from the database table mapped to this model."""
        table = cls.get_table()
        rows = DB.query(f"SELECT * FROM {table}")
        return [cls(**row) for row in rows]

    @classmethod
    def find(cls, pk_value: Any) -> Optional['Model']:
        """Finds a specific model record using its primary key."""
        table = cls.get_table()
        pk = cls.__primary_key__
        p = cls._placeholder()
        
        rows = DB.query(f"SELECT * FROM {table} WHERE {pk} = {p} LIMIT 1", (pk_value,))
        return cls(**rows[0]) if rows else None

    @classmethod
    def where(cls, column: str, value: Any, operator: str = "=") -> List['Model']:
        """Applies a basic conditional filtering constraint to the selection query."""
        table = cls.get_table()
        p = cls._placeholder()
        
        rows = DB.query(f"SELECT * FROM {table} WHERE {column} {operator} {p}", (value,))
        return [cls(**row) for row in rows]

    @classmethod
    def create(cls, **kwargs) -> 'Model':
        """Saves a new record into the database and returns the model instance."""
        instance = cls(**kwargs)
        instance.save()
        return instance

    def save(self) -> 'Model':
        """Performs a dynamic INSERT or UPDATE routine based on object persistence state."""
        table = self.get_table()
        pk = self.__primary_key__
        p = self._placeholder()
        
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # Intercept and append automated timestamps if feature is enabled
        if self.has_timestamps:
            if pk not in self._attributes or self._attributes[pk] is None:
                self._attributes['created_at'] = now
            self._attributes['updated_at'] = now

        # Isolate payload attributes from identity keys
        attrs = {k: v for k, v in self._attributes.items() if k != pk or v is not None}
        columns = list(attrs.keys())
        values = tuple(attrs.values())

        if pk in self._attributes and self._attributes[pk] is not None:
            # UPDATE Action
            set_clause = ", ".join([f"{col} = {p}" for col in columns])
            sql = f"UPDATE {table} SET {set_clause} WHERE {pk} = {p}"
            DB.query(sql, values + (self._attributes[pk],))
        else:
            # INSERT Action
            placeholders = ", ".join([p] * len(columns))
            cols_clause = ", ".join(columns)
            sql = f"INSERT INTO {table} ({cols_clause}) VALUES ({placeholders})"
            
            new_id = DB.query(sql, values)
            self._attributes[pk] = new_id

        return self

    def delete(self) -> bool:
        """Removes the current model record from the database storage layer."""
        pk = self.__primary_key__
        p = self._placeholder()
        
        if pk in self._attributes and self._attributes[pk] is not None:
            table = self.get_table()
            DB.query(f"DELETE FROM {table} WHERE {pk} = {p}", (self._attributes[pk],))
            self._attributes[pk] = None
            return True
        return False

    # -------------------------------------------------------------------------
    # Relationship Handlers
    # -------------------------------------------------------------------------

    def has_many(self, related_class: Any, foreign_key: Optional[str] = None, local_key: Optional[str] = None) -> List[Any]:
        """Defines a one-to-many relationship relationship structure mapping downstream models."""
        fk = foreign_key or f"{self.__class__.__name__.lower()}_id"
        lk = local_key or self.__primary_key__
        return related_class.where(fk, getattr(self, lk))

    def belongs_to(self, related_class: Any, foreign_key: Optional[str] = None, owner_key: Optional[str] = None) -> Optional[Any]:
        """Defines an inverse structural assignment pointing up to a parent model layer."""
        fk = foreign_key or f"{related_class.__name__.lower()}_id"
        ok = owner_key or related_class.__primary_key__
        
        results = related_class.where(ok, getattr(self, fk))
        return results[0] if results else None