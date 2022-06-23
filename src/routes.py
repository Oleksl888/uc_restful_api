from src import api
from src.resources.authentication import RegisterApi, LoginApi
from src.resources.feedback import FeedbackApi
from src.resources.ingredients import IngredientApi
from src.resources.recipe import RecipeApi
from src.resources.smoke import Smoke
from src.resources.users import UsersApi


api.add_resource(Smoke, '/smoke', strict_slashes=False)
api.add_resource(RecipeApi, '/recipes', '/recipes/<_id>', strict_slashes=False)
api.add_resource(IngredientApi, '/ingredients', '/ingredients/<_id>', strict_slashes=False)
api.add_resource(RegisterApi, '/register', strict_slashes=False)
api.add_resource(LoginApi, '/login', strict_slashes=False)
api.add_resource(FeedbackApi, '/feedback', strict_slashes=False)
api.add_resource(UsersApi, '/users', '/users/<uuid>', strict_slashes=False)