from flask import request
from flask_restful import Resource
from sqlalchemy.orm import selectinload
from src import db
from src.models import Recipe, Ingredient
from src.resources.iptracker import add_tracker
from src.schemas import RecipeSchema


class SearchApi(Resource):
    recipe_schema = RecipeSchema()

    @add_tracker
    def get(self):
        """Search is available by recipe name or ingredient name.
        Search will return all recipes that contain recipe query or that contain all ingredient names"""
        recipe_query = request.args.get('recipe')
        ingredient_query = request.args.get('ingredient')
        if not recipe_query and not ingredient_query:
            recipes = db.session.query(Recipe).options(
                selectinload(Recipe.ingredients), selectinload(Recipe.feedback)).all()
            recipes_data = self.recipe_schema.dump(recipes, many=True)
            return recipes_data, 200
        elif recipe_query:
            recipes = db.session.query(Recipe).filter(
                Recipe.name.like(f'%{recipe_query.lower()}%')).all()
            if not recipes:
                return {'message': 'Recipe not found'}, 404
            else:
                recipe_data = self.recipe_schema.dump(recipes, many=True)
                return recipe_data, 200
        elif ingredient_query:
            ingredient_list = [name.strip() for name in ingredient_query.split(',')]  # Getting a list of ingredients
            recipes = db.session.query(Recipe).options(
                selectinload(Recipe.ingredients), selectinload(Recipe.feedback)).all()
            recipes_data = self.recipe_schema.dump(recipes, many=True)  # Getting a list of all recipes
            new_data = []
            for recipe in recipes_data:  # Iterating through the list of recipes to match the ingredients
                ing_list = recipe.get('ingredients')
                counter = 0
                for entry in ingredient_list:
                    for item in ing_list:
                        if entry in item.get('name'):
                            counter += 1
                if counter == len(ingredient_list):  # If requirements met a recipe will be added to new list
                    new_data.append(recipe)
            if not new_data:
                return {'message': 'Recipes not found'}, 404
            else:
                return new_data, 200
