from flask import request
from flask_restful import Resource
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError, DatabaseError

from src import db
from src.models import Ingredient, Recipe
from src.resources.authentication import jwt_protected
from src.resources.iptracker import add_tracker
from src.schemas import IngredientSchema

#Refactor the code to throw an excception in the beginning
def normalize_data(data_from_json):
    """
    Removes trailing characters and sets all strings to lower case before adding them to db.
    Empty strings will be removed from recipe list if found or set to None if found in ingredient name.
    If ingedient name field is empty raises a Validation Error
    """
    if not data_from_json.get('name') or len(data_from_json.get('name')) < 1:
        raise ValidationError
    for key, val in data_from_json.items():
        if key == 'recipes':
            new_list = [item.strip().lower() for item in val if len(item) > 0]
            data_from_json[key] = new_list
        else:
            data_from_json[key] = val.strip().lower() if len(val) > 0 else None


class IngredientApi(Resource):
    ingredient_schema = IngredientSchema()

    @add_tracker
    def get(self, _id=None):
        if not _id:
            ingredients = db.session.query(Ingredient).all()  # Checking for all ingredients in db
            ingredients_data = self.ingredient_schema.dump(ingredients, many=True)  # Loading result to JSON
            return ingredients_data, 200
        else:
            ingredient = db.session.query(Ingredient).filter_by(id=_id).first()  # Checking for ingredients by ID in db
            if not ingredient:
                return {'message': 'Ingredient not found'}, 404
            else:
                ingredient_data = self.ingredient_schema.dump(ingredient)
                return ingredient_data, 200

    @jwt_protected
    def post(self):
        """
        If recipe is in request, checks if this recipe exists in database.
        If not exists this method DOES NOT create a new recipe, just creates a new ingredient with no link to recipe.
        If recipe exists it's being linked to new ingredient.
        """
        data = request.json  # Getting data from json object
        try:
            normalize_data(data)  # Normalizing data
        except ValidationError:
            return {'message': 'Incorrect data entered: name filed cannot be empty'}, 400
        recipes = data.get('recipes', None)  # Checking for recipes in request
        if not recipes:  # Using default schema load scenario if no recipes are attached to the request
            try:
                ingredient = self.ingredient_schema.load(data, session=db.session)
            except ValidationError:
                return {'message': 'Incorrect data entered'}, 400
            except (KeyError, TypeError, ValueError, AttributeError, DatabaseError):
                print('Wrong data. Database error, cleaning up remaining files...')
                db.session.rollback()
                db.session.close()
            else:
                try:
                    db.session.add(ingredient)
                    db.session.commit()
                except IntegrityError:
                    return {'message': 'The ingredient already exists'}, 409
                return {'message': 'Ingredient has been added'}, 201
        else:  # Scenario when recipes list is attached to request
            ingredient_name = data.get('name', None)
            ingredient = Ingredient(ingredient_name)  # Creating ingredient instance with name from request
            for item in recipes:  # Iterating over data in recipes and instantiating recipes if found
                recipe = db.session.query(Recipe).filter_by(name=item).first()
                if not recipe:
                    continue
                ingredient.recipes.append(recipe)
            try:
                db.session.add(ingredient)
                db.session.commit()
            except ValidationError:
                return {'message': 'Incorrect data entered'}, 400
            except IntegrityError:
                return {'message': 'The ingredient already exists'}, 409
            except (KeyError, TypeError, ValueError, AttributeError, DatabaseError):
                print('Wrong data. Database error, cleaning up remaining files...')
                db.session.rollback()
                db.session.close()
            else:
                return {'message': 'Ingredient has been created with recipes'}, 201

    @jwt_protected
    def put(self, _id=None):
        data = request.json
        try:
            normalize_data(data)  # Normalizing data
        except ValidationError:
            return {'message': 'Incorrect data entered: name filed cannot be empty'}, 400
        if _id is None:
            return {'message': 'Must specify ingredient id in the url to make changes'}, 404
        ingredient = db.session.query(Ingredient).filter_by(id=_id).first()
        if not ingredient:
            return {'message': 'The ingredient does not yet exist'}, 404
        recipes = data.get('recipes', None)
        if not recipes:
            try:
                ingredient = self.ingredient_schema.load(data, instance=ingredient, session=db.session)
            except ValidationError:
                return {'message': 'Incorrect data entered'}, 400
            except (KeyError, TypeError, ValueError, AttributeError, DatabaseError):
                print('Wrong data. Database error, cleaning up remaining files...')
                db.session.rollback()
                db.session.close()
            else:
                try:
                    db.session.add(ingredient)
                    db.session.commit()
                except IntegrityError:
                    return {'message': 'The ingredient already exists'}, 409
                return {'message': 'Ingredient has been updated'}, 201
        else:
            ingredient_name = data.get('name', None)
            ingredient.name = ingredient_name
            ingredient.recipes = []
            for item in recipes:
                recipe = db.session.query(Recipe).filter_by(name=item).first()
                if not recipe:
                    continue
                ingredient.recipes.append(recipe)
            try:
                db.session.commit()
            except IntegrityError:
                return {'message': 'The ingredient already exists'}, 409
            except (KeyError, TypeError, ValueError, AttributeError, ValidationError, DatabaseError):
                print('Wrong data. Database error, cleaning up remaining files...')
                db.session.rollback()
                db.session.close()
            else:
                return {'message': 'Ingredient has been updated with recipes'}, 201

    @jwt_protected
    def patch(self, _id=None):
        data = request.json
        try:   # Normalizing data in patch method as it can allow empty fields
            if data('name') or len(data.get('name')) < 1:
                raise ValidationError
            for key, val in data.items():
                if key == 'recipes':
                    new_list = [item.strip().lower() for item in val if len(item) > 0]
                    data[key] = new_list
                else:
                    data[key] = val.strip().lower() if len(val) > 0 else None
        except ValidationError:
            return {'message': 'Incorrect data entered: name field cannot be empty'}, 400
        if _id is None:
            return {'message': 'Must specify ingredient id in the url to make changes'}, 404
        ingredient = db.session.query(Ingredient).filter_by(id=_id).first()
        if not ingredient:
            return {'message': 'The ingredient does not yet exist'}, 404
        recipes = data.get('recipes', None)
        if not recipes:
            try:
                ingredient = self.ingredient_schema.load(data, instance=ingredient, session=db.session, partial=True)
            except ValidationError:
                return {'message': 'Incorrect data entered'}, 400
            except (KeyError, TypeError, ValueError, AttributeError, DatabaseError):
                print('Wrong data. Database error, cleaning up remaining files...')
                db.session.rollback()
                db.session.close()
            else:
                try:
                    db.session.add(ingredient)
                    db.session.commit()
                except IntegrityError:
                    return {'message': 'The ingredient already exists'}, 409
                return {'message': 'Ingredient has been updated'}, 201
        else:
            ingredient_name = data.get('name', None)
            ingredient.name = ingredient_name
            ingredient.recipes = []
            for item in recipes:
                recipe = db.session.query(Recipe).filter_by(name=item).first()
                if not recipe:
                    continue
                ingredient.recipes.append(recipe)
            try:
                db.session.commit()
            except IntegrityError:
                return {'message': 'The ingredient already exists'}, 409
            except (KeyError, TypeError, ValueError, AttributeError, ValidationError, DatabaseError):
                print('Wrong data. Database error, cleaning up remaining files...')
                db.session.rollback()
                db.session.close()
            else:
                return {'message': 'Ingredient has been updated with recipes'}, 201

    @jwt_protected
    def delete(self, _id=None):
        if _id is None:
            return {'message': 'Must specify ingredient id in the url to delete'}, 404
        ingredient = db.session.query(Ingredient).filter_by(id=_id).first()
        if not ingredient:
            return {'message': 'The ingredient does not yet exist'}, 404
        db.session.delete(ingredient)
        db.session.commit()
        return {'message': 'The ingredient has been deleted'}, 204
