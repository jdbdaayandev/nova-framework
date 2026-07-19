import os
import sqlite3
from engine.Support.env import env

class DatabaseConnection:
    _instance = None
    _connection = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseConnection, cls).__new__(cls)
        return cls._instance

    def connect(self):
        if self._connection is not None:
            return self._connection

        driver = env('DB_CONNECTION', 'sqlite').lower()

        if driver == 'sqlite':
            self._connection = self._connect_sqlite()
        elif driver == 'mysql':
            self._connection = self._connect_mysql()
        elif driver in ['postgres', 'pgsql', 'postgresql']:
            self._connection = self._connect_postgres()
        else:
            raise ValueError(f"❌ Unsupported database driver: {driver}")

        return self._connection

    def _connect_sqlite(self):
        db_path = env('DB_DATABASE', 'database/database.sqlite')
        db_dir = os.path.dirname(db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)
            
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row 
        return conn

    def _connect_mysql(self):
        try:
            import pymysql
            return pymysql.connect(
                host=env('DB_HOST', '127.0.0.1'),
                port=int(env('DB_PORT', 3306)),
                user=env('DB_USERNAME', 'root'),
                password=env('DB_PASSWORD', ''),
                database=env('DB_DATABASE', 'nova'),
                cursorclass=pymysql.cursors.DictCursor
            )
        except ImportError:
            raise ImportError("❌ To use MySQL: `pip install pymysql`")

    def _connect_postgres(self):
        try:
            import psycopg2
            from psycopg2.extras import RealDictCursor
            return psycopg2.connect(
                host=env('DB_HOST', '127.0.0.1'),
                port=int(env('DB_PORT', 5432)),
                user=env('DB_USERNAME', 'postgres'),
                password=env('DB_PASSWORD', ''),
                dbname=env('DB_DATABASE', 'nova'),
                cursor_factory=RealDictCursor
            )
        except ImportError:
            raise ImportError("❌ To use PostgreSQL: `pip install psycopg2-binary`")

    @property
    def placeholder(self):
        """Returns the correct parameter placeholder for the active driver."""
        driver = env('DB_CONNECTION', 'sqlite').lower()
        return '%s' if driver in ['mysql', 'postgres', 'pgsql', 'postgresql'] else '?'

    def query(self, sql: str, params: tuple = ()):
        """Unified query wrapper with automatic placeholder translation."""
        conn = self.connect()
        cursor = conn.cursor()
        
        # Translate '?' to '%s' if using MySQL/Postgres
        if self.placeholder == '%s':
            sql = sql.replace('?', '%s')
            
        cursor.execute(sql, params)
        
        # If modifying data, commit and return affected rows/id
        if sql.strip().upper().startswith(("INSERT", "UPDATE", "DELETE")):
            conn.commit()
            if sql.strip().upper().startswith("INSERT"):
                try:
                    return cursor.lastrowid
                except Exception:
                    # Fallback if driver doesn't support lastrowid out of the box
                    return cursor.rowcount
            return cursor.rowcount
            
        # If fetching data, return the results as standard dicts
        return [dict(row) for row in cursor.fetchall()]

DB = DatabaseConnection()