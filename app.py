from flask import Flask, jsonify, request
import os
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow 




app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///" + os.path.join(basedir, 'recipes.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
ma = Marshmallow(app)

# Flask CLI 
@app.cli.command('create_database')
def create_database():
    db.create_all()

    print('Database tables created')

@app.cli.command('seed_db')
def seed_database():
    user1 = User(email='admin@gmail.com', username='adminuser', is_admin=True)
    user2 = User(email='testuser@gmail.com', username='testuser', is_admin=False)
    recipe1 = Recipe(name='Roast_Chicken', protein='chicken', ingredients='chicken, onions, carrots, celery, garlic, oil, lemon, fresh herbs')
    recipe2 = Recipe(name='Creamy_Beef_Pasta', protein='beef', ingredients='beef, garlic, basil, oregano, salt, pepper, flour, tomato sauce, beef broth, pasta, heavy cream, cheddar cheese')
    db.session.add_all([user1, user2, recipe1, recipe2])
    db.session.commit()
    print('Database seeded')

@app.cli.command('destroy_database')
def destroy_databse():
    db.drop_all()
    print('Database tables destroyed')


# Database Models

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String, unique=True)
    username = db.Column(db.String)
    is_admin = db.Column(db.Boolean)

class Recipe(db.Model):
    __tablename__ = 'recipes'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True)
    protein = db.Column(db.String)
    ingredients = db.Column(db.String)


# Marshmallow Schema

class UserSchema(ma.SQLAlchemySchema):
    class Meta:
        model = User

    email = ma.auto_field()
    username = ma.auto_field()
    links = ma.auto_field()

    # Hyperlinks
    links = ma.Hyperlinks(
        {
        'self': ma.URLFor("user_detail", values=dict(username="<username>")),
        "collection": ma.URLFor("all_users"),
       }
    )

class RecipeSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Recipe

    name = ma.auto_field()
    protein = ma.auto_field()
    ingredients = ma.auto_field()
    links = ma.auto_field()

    # Hyperlinks
    links = ma.Hyperlinks(
        {
        'self': ma.URLFor("recipe_detail", values=dict(recipe_name="<name>")),
        "collection": ma.URLFor("all_recipes"),
       }
    )

# Define the ability to serialize objects
user_schema = UserSchema()
recipe_schema = RecipeSchema()

# Define the ability to serialize a collection of objects
users_schema = UserSchema(many=True)
recipes_schema = RecipeSchema(many=True)



# Main Code

@app.route('/')
def hello_world():
    return jsonify(message='hello world!')


@app.route('/not_found')
def not_found():
    return jsonify(message='Resource not found'), 404

@app.route('/name')
def name():
    username = request.args.get('username')
    return jsonify(message=f'your name is {username}')


@app.route('/recipes/', methods=['GET', 'POST'])
def all_recipes():
    """
    Supports GET and POST methods 
    GET: Returns a list of all recipes 
    POST: Adds a new recipe to the database
    """
    if request.method == 'POST':
        pass
    
    # Code for GET request
    recipes = Recipe.query.all()
    return jsonify(recipes_schema.dump(recipes))

@app.route('/recipes/<string:recipe_name>', methods=['GET', 'PUT', 'DELETE'])
def recipe_detail(recipe_name:str):
    """
    Supports GET, PUT, DELETE methods for admin user
    All other users are only allowed GET
    GET: Returns recipe data for the given recipe
    PUT: Modifies recipe data for the given recipe
    DELETE: Deletes the given 

    """
    if request.method == 'PUT':
        pass
    elif request.method == 'DELETE':
        pass
    
    # Code for GET request
    recipe = Recipe.query.filter_by(name=recipe_name).first()
    return recipe_schema.dump(recipe)

@app.route('/users/', methods=['GET', 'POST'])
def all_users():
    """
    Only the admin user can access this endpoint
    Supports GET and POST methods for admin user 
    GET: Returns a list of all users
    POST: Adds a new user to the database
    """
    if request.method == 'POST':
        pass
    
    # Code for GET method

    users_list = User.query.all()
    return jsonify(users_schema.dump(users_list))

@app.route('/users/<string:username>', methods=['GET', 'PUT', 'DELETE'])
def user_detail(username:str):
    """
    Accessible by admin user and the normal users. Normal users can only access their own account
    Supports GET, PUT, DELETE methods
    GET: Returns user data for the given user
    PUT: Modifies user data for the given user
    DELETE: Deletes the given 

    """
    if request.method == 'PUT':
        pass
    elif request.method == 'DELETE':
        pass
    
    # Code for GET method
    user = User.query.filter_by(username=username).first()
    return user_schema.dump(user)











if __name__ == '__main__':
    app.run()



