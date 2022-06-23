from flask import request
from flask_restful import Resource
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError, DatabaseError

from src import db
from src.models import Ingredient, Recipe
from src.resources.iptracker import add_tracker
from src.schemas import IngredientSchema


class IngredientApi(Resource):
    ingredient_schema = IngredientSchema()

    @add_tracker
    def get(self, _id=None):
        if not _id:
            ingredients = db.session.query(Ingredient).all()
            ingredients_data = self.ingredient_schema.dump(ingredients, many=True)
            return ingredients_data, 200
        else:
            ingredient = db.session.query(Ingredient).filter_by(id=_id).first()
            if not ingredient:
                return {'message': 'Ingredient not found'}, 404
            else:
                ingredient_data = self.ingredient_schema.dump(ingredient)
                return ingredient_data, 200

    def post(self):
        data = request.json
        # check if recipe is in the request, create appropriate objects and add them to db
        recipes = data.get('recipes', None)
        if not recipes:
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
        else:
            ingredient_name = data.get('name', None)
            ingredient = Ingredient(ingredient_name)
            for item in recipes:
                recipe = db.session.query(Recipe).filter_by(name=item.strip().lower()).first()
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

    def put(self, _id=None):
        data = request.json
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
            ingredient_name = data.get('name', "")
            if len(ingredient_name) < 1:
                return {'message': 'Incorrect data entered: Mandatory fields cannot be empty'}, 400
            ingredient.name = ingredient_name
            ingredient.recipes = []
            for item in recipes:
                recipe = db.session.query(Recipe).filter_by(name=item.strip().lower()).first()
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

    def patch(self, _id=None):
        data = request.json
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
            if ingredient_name and len(ingredient_name) > 0:
                ingredient.name = ingredient_name
            ingredient.recipes = []
            for item in recipes:
                recipe = db.session.query(Recipe).filter_by(name=item.strip().lower()).first()
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

    def delete(self, _id=None):
        if _id is None:
            return {'message': 'Must specify ingredient id in the url to delete'}, 404
        ingredient = db.session.query(Ingredient).filter_by(id=_id).first()
        if not ingredient:
            return {'message': 'The ingredient does not yet exist'}, 404
        db.session.delete(ingredient)
        db.session.commit()
        return {'message': 'The ingredient has been deleted'}, 204
