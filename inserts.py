import os

from flask_mail import Message

from src import db, mail, app
from src.models import Recipe, Ingredient, Feedback, User #, RecipeFeedback


def db_populate():

    # recipe = Recipe('borsh', 'some good stuff')
    # ingredient1 = Ingredient('beets')
    # ingredient1.recipes.append(recipe)
    # ingredient2 = Ingredient('potato')
    # ingredient2.recipes.append(recipe)
    # ingredient3 = Ingredient('water')
    # ingredient3.recipes.append(recipe)
    # ingredient4 = Ingredient('love')
    # ingredient4.recipes.append(recipe)
    # recipe.ingredients = [ingredient1, ingredient2, ingredient3, ingredient4]
    # db.session.add(ingredient1)
    # db.session.add(ingredient2)
    # db.session.add(ingredient3)
    # db.session.add(ingredient4)
    # feedback = Feedback('alex', 'test message')
    # recipe.feedback.append(feedback)
    # db.session.add(recipe)
    # db.session.commit()
    # recipe = db.session.query(Recipe).filter_by(id=1).first()
    # db.session.delete(recipe)
    # db.session.commit()
    # user = User('alex', 'aslyusarenko@gmail.com', '12345678')
    # feedback = Feedback('alex', 'another test message')
    # user.feedback.append(feedback)
    # db.session.add(user)
    # db.session.commit()

    recipe = Recipe('chebureks', 'somethijng totaly different')
    ingredient1 = db.session.query(Ingredient).filter_by(name='beets').first()
    if not ingredient1:
        ingredient1 = Ingredient('beets')
    ingredient1.recipes.append(recipe)
    ingredient2 = db.session.query(Ingredient).filter_by(name='tears').first()
    if not ingredient2:
        ingredient2 = Ingredient('tears')
    ingredient2.recipes.append(recipe)
    ingredient3 = db.session.query(Ingredient).filter_by(name='bleat').first()
    if not ingredient3:
        ingredient3 = Ingredient('bleat')
    ingredient3.recipes.append(recipe)
    ingredient4 = db.session.query(Ingredient).filter_by(name='salt').first()
    if not ingredient4:
        ingredient4 = Ingredient('salt')
    ingredient4.recipes.append(recipe)
    db.session.add(recipe)
    db.session.commit()


def send_mail(_name, _email):
    print('Sending mail...')
    message = Message(
        subject='You have been registered',
        recipients=[_email],
        sender="olesliusarenko@gmail.com",
        body=f'Hello, {_name}! You have been registered.'
    )
    mail.send(message)
    print('Email sent successfully...')
    return 'success'


if __name__ == '__main__':
    with app.app_context():
        send_mail('Alex', 'aslyusarenko@gmail.com')
