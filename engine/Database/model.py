from engine.Database.connection import DB

class Model:
    """
    Nova-ORM Base Model
    Implements Active Record pattern for easy database interactions.
    """
    __table__ = None
    __primary_key__ = 'id'

    def __init__(self, **kwargs):
        super().__setattr__('_attributes', kwargs)

    def __getattr__(self, key):
        if key in self._attributes:
            return self._attributes[key]
        raise AttributeError(f"'{self.__class__.__name__}' has no attribute '{key}'")

    def __setattr__(self, key, value):
        if key.startswith('_') or key in ['__table__', '__primary_key__']:
            super().__setattr__(key, value)
        else:
            self._attributes[key] = value

    @classmethod
    def get_table(cls):
        """Resolves the table name. Defaults to lowercase class name + 's'."""
        return cls.__table__ or f"{cls.__name__.lower()}s"

    @classmethod
    def all(cls):
        table = cls.get_table()
        rows = DB.query(f"SELECT * FROM {table}")
        return [cls(**row) for row in rows]

    @classmethod
    def find(cls, pk_value):
        table = cls.get_table()
        pk = cls.__primary_key__
        rows = DB.query(f"SELECT * FROM {table} WHERE {pk} = ? LIMIT 1", (pk_value,))
        return cls(**rows[0]) if rows else None

    @classmethod
    def where(cls, column, value, operator="="):
        table = cls.get_table()
        rows = DB.query(f"SELECT * FROM {table} WHERE {column} {operator} ?", (value,))
        return [cls(**row) for row in rows]

    @classmethod
    def create(cls, **kwargs):
        instance = cls(**kwargs)
        instance.save()
        return instance

    def save(self):
        table = self.get_table()
        pk = self.__primary_key__
        
        attrs = {k: v for k, v in self._attributes.items() if k != pk or v is not None}
        columns = list(attrs.keys())
        values = tuple(attrs.values())

        if pk in self._attributes and self._attributes[pk] is not None:
            # UPDATE
            set_clause = ", ".join([f"{col} = ?" for col in columns])
            sql = f"UPDATE {table} SET {set_clause} WHERE {pk} = ?"
            DB.query(sql, values + (self._attributes[pk],))
        else:
            # INSERT
            placeholders = ", ".join(["?"] * len(columns))
            cols_clause = ", ".join(columns)
            sql = f"INSERT INTO {table} ({cols_clause}) VALUES ({placeholders})"
            
            new_id = DB.query(sql, values)
            self._attributes[pk] = new_id

        return self

    def delete(self):
        pk = self.__primary_key__
        if pk in self._attributes and self._attributes[pk] is not None:
            table = self.get_table()
            DB.query(f"DELETE FROM {table} WHERE {pk} = ?", (self._attributes[pk],))
            self._attributes[pk] = None
            return True
        return False

    # --- Relationships ---

    def has_many(self, related_class, foreign_key=None, local_key=None):
        """Fetches related records where the related table holds the foreign key."""
        fk = foreign_key or f"{self.__class__.__name__.lower()}_id"
        lk = local_key or self.__primary_key__
        return related_class.where(fk, getattr(self, lk))

    def belongs_to(self, related_class, foreign_key=None, owner_key=None):
        """Fetches a single parent record."""
        fk = foreign_key or f"{related_class.__name__.lower()}_id"
        ok = owner_key or related_class.__primary_key__
        return related_class.where(ok, getattr(self, fk))[0] if getattr(self, fk) else None