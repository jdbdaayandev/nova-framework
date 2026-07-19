from engine.Http.request import Request
from engine.Http.response import Response
from engine.View.view import view
from app.Models.User import User
from app.Actions.CreateUserAction import CreateUserAction

class UserController:
    def index(self, request: Request) -> Response:
        users = User.all()
        html = view('users.index', {'users': users})
        return Response(html, status=200)

    def store(self, request: Request) -> Response:
        """Handle a POST request to create a user."""
        
        # In our framework, request.query handles URL parameters like ?name=John
        # For simplicity in this step, we'll pretend the data came from a form POST
        data = {
            'name': request.input('name', 'Anonymous'),
            'email': request.input('email', 'anon@example.com')
        }

        try:
            # Instantiate the Action and execute the logic
            action = CreateUserAction()
            new_user = action.execute(data)
            
            return Response(f"User {new_user['name']} created successfully!", status=201)
            
        except ValueError as e:
            return Response(str(e), status=400)