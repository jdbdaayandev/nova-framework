from app.Models.User import User

class CreateUserAction:
    def execute(self, data: dict) -> dict:
        """
        Execute the business logic to create a user.
        In a real app, you would hash the password, trigger a welcome email, etc.
        """
        # Validate data (simplified)
        if 'name' not in data or 'email' not in data:
            raise ValueError("Name and email are required.")

        # Trigger the Model to save to the database
        new_user = User.create(data['name'], data['email'])
        
        # You could dispatch an event or send an email right here
        # send_welcome_email(new_user['email'])

        return new_user