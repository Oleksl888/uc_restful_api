from flask import request
from flask_restful import Resource
from sqlalchemy.orm import selectinload
from sqlalchemy.exc import IntegrityError, DatabaseError
from marshmallow.exceptions import ValidationError
from src import db
from src.models import Recipe, Ingredient
from src.resources.authentication import jwt_protected
from src.resources.iptracker import add_tracker
from src.schemas import RecipeSchema


def normalize_data(data_from_json):
    """
    Removes trailing characters and sets all strings to lower case before adding them to db.
    Empty strings will be removed from recipe list if found or set to None if found in ingredient name.
    If recipe name field is empty raises a Validation Error
    """
    if not data_from_json.get('name') or len(data_from_json.get('name')) < 1:
        raise ValidationError
    if not data_from_json.get('recipe') or len(data_from_json.get('recipe')) < 1:
        raise ValidationError
    for key, val in data_from_json.items():
        if key == 'ingredients':
            new_list = [item.strip().lower() for item in val if len(item) > 0]
            data_from_json[key] = new_list
        elif key == 'recipe':
            continue
        else:
            data_from_json[key] = val.strip().lower() if len(val) > 0 else None


class RecipeApi(Resource):
    recipe_schema = RecipeSchema()

    @add_tracker
    def get(self, _id=None):
        if not _id:
            recipes = db.session.query(Recipe).options(
                selectinload(Recipe.ingredients), selectinload(Recipe.feedback)).all()
            recipes_data = self.recipe_schema.dump(recipes, many=True)
            return recipes_data, 200
        else:
            recipe = db.session.query(Recipe).filter_by(id=_id).first()
            if not recipe:
                return {'message': 'Recipe not found'}, 404
            else:
                recipe_data = self.recipe_schema.dump(recipe)
                return recipe_data, 200

    @jwt_protected
    def post(self):
        data = request.json
        try:
            normalize_data(data)
        except ValidationError:
            return {'message': 'Incorrect data entered: name and recipe field cannot be empty'}, 400
        ingredients = data.get('ingredients', None)
        if not ingredients:
            try:
                recipe = self.recipe_schema.load(data, session=db.session)
            except ValidationError:
                return {'message': 'Incorrect data entered'}, 400
            except (KeyError, TypeError, ValueError, AttributeError, DatabaseError):
                print('Wrong data. Database error, cleaning up remaining files...')
                db.session.rollback()
                db.session.close()
            else:
                try:
                    db.session.add(recipe)
                    db.session.commit()
                except IntegrityError:
                    return {'message': 'The recipe already exists'}, 409
                return {'message': 'Recipe has been added'}, 201
        else:
            recipe_name = data.get('name')
            recipe_text = data.get('recipe')
            recipe = Recipe(recipe_name, recipe_text)
            for item in ingredients:
                ingredient = db.session.query(Ingredient).filter_by(name=item).first()
                if not ingredient:
                    ingredient = Ingredient(item)
                recipe.ingredients.append(ingredient)
            try:
                db.session.add(recipe)
                db.session.commit()
            except IntegrityError:
                return {'message': 'The recipe already exists'}, 409
            except (KeyError, TypeError, ValueError, AttributeError, ValidationError, DatabaseError):
                print('Wrong data. Database error, cleaning up remaining files...')
                db.session.rollback()
                db.session.close()
            else:
                return {'message': 'Recipe has been created with ingredients'}, 201

    @jwt_protected
    def put(self, _id=None):
        data = request.json
        try:
            normalize_data(data)
        except ValidationError:
            return {'message': 'Incorrect data entered: name and recipe field cannot be empty'}, 400
        if _id is None:
            return {'message': 'Must specify recipe id in the url to make changes'}, 404
        recipe = db.session.query(Recipe).filter_by(id=_id).first()
        if not recipe:
            return {'message': 'The recipe does not yet exist'}, 404
        ingredients = data.get('ingredients', None)
        if not ingredients:
            try:
                recipe = self.recipe_schema.load(data, instance=recipe, session=db.session)
            except ValidationError:
                return {'message': 'Incorrect data entered'}, 400
            except (KeyError, TypeError, ValueError, AttributeError, DatabaseError):
                print('Wrong data. Database error, cleaning up remaining files...')
                db.session.rollback()
                db.session.close()
            else:
                try:
                    db.session.add(recipe)
                    db.session.commit()
                except IntegrityError:
                    return {'message': 'The recipe already exists'}, 409
                return {'message': 'Recipe has been updated'}, 201
        else:
            recipe_name = data.get('name', '')
            recipe_text = data.get('recipe', '')
            recipe.name = recipe_name
            recipe.recipe = recipe_text
            recipe.ingredients = []
            for item in ingredients:
                ingredient = db.session.query(Ingredient).filter_by(name=item).first()
                if not ingredient:
                    ingredient = Ingredient(item)
                recipe.ingredients.append(ingredient)
            try:
                db.session.commit()
            except IntegrityError:
                return {'message': 'The recipe already exists'}, 409
            except (KeyError, TypeError, ValueError, AttributeError, ValidationError, DatabaseError):
                print('Wrong data. Database error, cleaning up remaining files...')
                db.session.rollback()
                db.session.close()
            else:
                return {'message': 'Recipe has been updated with ingredients'}, 201

    @jwt_protected
    def patch(self, _id=None):
        data = request.json
        try:  # Validating and normalizing data - made separate for patch method
            if data.get('name') and len(data.get('name')) < 1:
                raise ValidationError
            if data.get('recipe') and len(data.get('recipe')) < 1:
                raise ValidationError
            for key, val in data.items():
                if key == 'ingredients':
                    new_list = [item.strip().lower() for item in val if len(item) > 0]
                    data[key] = new_list
                elif key == 'recipe':
                    continue
                else:
                    data[key] = val.strip().lower() if len(val) > 0 else None
        except ValidationError:
            return {'message': 'Incorrect data entered: name and recipe fields cannot be empty'}, 400
        if _id is None:
            return {'message': 'Must specify recipe id in the url to make changes'}, 404
        recipe = db.session.query(Recipe).filter_by(id=_id).first()
        if not recipe:
            return {'message': 'The recipe does not yet exist'}, 404
        ingredients = data.get('ingredients', None)
        if not ingredients:
            try:
                recipe = self.recipe_schema.load(data, instance=recipe, session=db.session, partial=True)
            except ValidationError:
                return {'message': 'Incorrect data entered'}, 400
            except (KeyError, TypeError, ValueError, AttributeError, DatabaseError):
                print('Wrong data. Database error, cleaning up remaining files...')
                db.session.rollback()
                db.session.close()
            else:
                try:
                    db.session.add(recipe)
                    db.session.commit()
                except IntegrityError:
                    return {'message': 'The recipe already exists'}, 409
                return {'message': 'Recipe has been updated'}, 201
        else:
            recipe_name = data.get('name', None)
            recipe_text = data.get('recipe', None)
            if recipe_name and len(recipe_name) > 0:
                recipe.name = recipe_name
            if recipe_text and len(recipe_text) > 0:
                recipe.recipe = recipe.text
            recipe.ingredients = []
            for item in ingredients:
                ingredient = db.session.query(Ingredient).filter_by(name=item.strip().lower()).first()
                if not ingredient:
                    ingredient = Ingredient(item.strip().lower())
                recipe.ingredients.append(ingredient)
            try:
                db.session.commit()
            except IntegrityError:
                return {'message': 'The recipe already exists'}, 409
            except (KeyError, TypeError, ValueError, AttributeError, ValidationError, DatabaseError):
                print('Wrong data. Database error, cleaning up remaining files...')
                db.session.rollback()
                db.session.close()
            else:
                return {'message': 'Recipe has been updated with ingredients'}, 201

    @jwt_protected
    def delete(self, _id=None):
        if _id is None:
            return {'message': 'Must specify recipe id in the url to delete'}, 404
        recipe = db.session.query(Recipe).filter_by(id=_id).first()
        if not recipe:
            return {'message': 'The recipe does not yet exist'}, 404
        db.session.delete(recipe)
        db.session.commit()
        return {'message': 'The recipe has been deleted'}, 204
