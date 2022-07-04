import csv
import os
import sys

from src import db, DATA_PATH, app
from src.models import Recipe, Ingredient
from sqlalchemy.exc import IntegrityError, DatabaseError


def read_csv(filename):
    """This function opens csv file, reads it into a dictionary and converts in json format"""
    try:
        with open(filename, encoding='utf8') as file:
            cook_book_list = []
            reader = csv.DictReader(file)
            for row in reader:
                cook_book_list.append(row)
    except FileNotFoundError:
        return {}
    else:
        return cook_book_list


def load_recipe_from_file(name):
    read_recipe = ''
    with open(os.path.join(DATA_PATH, 'recipes.txt'), encoding='utf-8-sig') as file:
        for line in file:
            if line.strip().lower() == name.lower():
                while len(line) > 1:
                    line = file.readline()
                    read_recipe += line
                return read_recipe
    return '''
The recipe is unavailable
Рецепт не знайдено
ʻaʻole i loaʻa ka meaʻai
Oideas gan aimsiú
Ricetta non trovata
Receta no encontrada
找不到食谱
레시피를 찾을 수 없습니다
Te tunu kaore i kitea
कृती सापडली नाही
Recept niet gevonden
Rezept nicht gefunden
Nie znaleziono przepisu
Рецепт не найден
Recette introuvable
    '''


@app.cli.command('db_initialize')
def initialize_db():
    '''Seeds the Database with the below command:
        <flask db_initialize>
    Make sure to create database prior to this with the below commands:
        <flask db init>
        <flask db migrate>
        <flask db upgrade>
    '''
    data_for_db = read_csv(os.path.join(DATA_PATH, 'cookbook.csv'))
    print('Populating Database...')
    try:
        for entry in data_for_db:
            recipe_text = load_recipe_from_file(entry['name'])
            recipe = Recipe(name=entry['name'], recipe=recipe_text)
            ingredients = [ingredient.strip() for ingredient in entry['ingredients'].split(',')]
            for ingredient in ingredients:
                test_ingredient = db.session.query(Ingredient).filter_by(name=ingredient).first()
                if not test_ingredient:
                    _ingredient = Ingredient(name=ingredient)
                    recipe.ingredients.append(_ingredient)
                else:
                    recipe.ingredients.append(test_ingredient)
            db.session.add(recipe)
            db.session.commit()
    except(KeyError, TypeError, ValueError, IndexError, AttributeError, IntegrityError, DatabaseError):
        print('Fatal database error, cleaning up remaining files...')
        print(sys.exc_info())
        db.session.rollback()
        db.session.close()
        os.remove(os.path.join(DATA_PATH, 'cook.db'))
        print('Closing app...')
        exit()
    else:
        print('Database Populated!')

