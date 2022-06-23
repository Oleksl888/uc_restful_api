import uuid
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from werkzeug.security import generate_password_hash
from src import db

#add nullable contrsaints
class Recipe(db.Model):
    __tablename__ = 'recipes'
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    recipe = Column(String, nullable=False)
    ingredients = db.relationship('Ingredient', secondary='recipe_ingredients',
                                  lazy=True, backref=db.backref('recipes', lazy=True))
    feedback = db.relationship('Feedback', secondary='recipe_feedback', lazy=True,
                               backref=db.backref('recipes', lazy=True))

    def __init__(self, name: str, recipe: str, ingredients=None, feedback=None):
        self.name = name
        self.recipe = recipe
        self.ingredients = [] if not ingredients else ingredients
        self.feedback = [] if not feedback else feedback

    def __repr__(self):
        return f'Recipe for <{self.name}>, {self.ingredients}'


class Ingredient(db.Model):
    __tablename__ = 'ingredients'
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)

    def __init__(self, name: str, recipes=None):
        self.name = name
        self.recipes = [] if not recipes else recipes

    def __repr__(self):
        return f'Ingredient <{self.name}>'


recipe_ingredients = db.Table(
    'recipe_ingredients',
    Column('recipe_id', Integer, ForeignKey('recipes.id'), primary_key=True),
    Column('ingredient_id', Integer, ForeignKey('ingredients.id'), primary_key=True)
)


class Feedback(db.Model):
    __tablename__ = 'feedback'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    message = Column(String, nullable=False)
    date_time = Column(DateTime)
    registered_user = Column(Boolean, default=False)

    def __init__(self, name: str, message: str, registered_user=False):
        self.name = name
        self.message = message
        self.date_time = datetime.now()
        self.registered_user = registered_user

    def __repr__(self):
        return f'Feedback object'


class Tracker(db.Model):
    __tablename__ = 'iptracker'
    id = Column(Integer, primary_key=True)
    ipaddress = Column(String)
    city = Column(String)
    country = Column(String)
    date_time = Column(DateTime)
    action = Column(String, default='Visit')

    def __init__(self, ipaddress: str, city: str, country: str, action=None):
        self.ipaddress = ipaddress
        self.city = city
        self.country = country
        self.date_time = datetime.now()
        self.action = 'Visit' if not action else action

    def __repr__(self):
        return f'Iptracker <{self.ipaddress}>, <{self.city}>, <{self.country}>'


class User(db.Model):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password = Column(String)
    uuid = Column(String)
    registered_date = Column(DateTime)
    current_login = Column(DateTime)
    last_login = Column(DateTime)
    userpic = Column(String)
    is_admin = Column(Boolean, default=False)
    feedback = db.relationship('Feedback', secondary='user_feedback', lazy='subquery', backref=db.backref('users', lazy=True))

    def __init__(self, name: str, email: str, password: str, feedback=None):
        self.name = name
        self.email = email
        self.password = generate_password_hash(password)
        self.registered_date = datetime.now()
        self.uuid = str(uuid.uuid4())
        self.feedback = [] if not feedback else feedback

    def __repr__(self):
        return f'User <{self.name}>, Email <{self.email}>'


recipe_feedback = db.Table(
    'recipe_feedback',
    Column('recipe_id', Integer, ForeignKey('recipes.id'), primary_key=True),
    Column('feedback_id', Integer, ForeignKey('feedback.id'), primary_key=True),
)


user_feedback = db.Table(
    'user_feedback',
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('feedback_id', Integer, ForeignKey('feedback.id'), primary_key=True),
)
