class User:
    # Simulating a database table in memory
    _db = [
        {'id': 1, 'name': 'Taylor Otwell', 'email': 'taylor@laravel.com'},
        {'id': 2, 'name': 'Guido van Rossum', 'email': 'guido@python.org'}
    ]

    @classmethod
    def all(cls):
        return cls._db

    @classmethod
    def create(cls, name: str, email: str) -> dict:
        new_id = len(cls._db) + 1
        new_user = {'id': new_id, 'name': name, 'email': email}
        cls._db.append(new_user)
        return new_user