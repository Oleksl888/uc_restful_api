from src import ma
from marshmallow import fields

from src.models import User, Feedback, Recipe, Ingredient


class RecipeSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Recipe
        exclude = ['id']
        load_instance = True
    ingredients = ma.Nested('IngredientSchema', many=True, only=('name',))
    feedback = ma.Nested('FeedbackSchema', many=True, only=('name', 'message'))


class IngredientSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Ingredient
        exclude = ['id']
        load_instance = True
    recipes = ma.Nested('RecipeSchema', many=True, only=('name',))


class FeedbackSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Feedback
        load_instance = True
        exclude = ['id']
    name = fields.String(required=True)
    message = fields.String(required=True)


class TrackerSchema(ma.Schema):
    class Meta:
        fields = ('id', 'ipaddress', 'city', 'country', 'date_time', 'action')
        load_instance = True


class UserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = User
        load_only = ['password']
        load_instance = True
    name = fields.String(required=True)
    email = fields.Email(required=True)
    password = fields.String(required=True)
    feedback = ma.Nested('FeedbackSchema', many=True, only=('message',))
