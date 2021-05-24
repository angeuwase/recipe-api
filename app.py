from flask import Flask, jsonify, request
import os
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow 
from flask_jwt_extended import JWTManager, create_access_token, get_jwt_identity, jwt_required




app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///" + os.path.join(basedir, 'recipes.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'super jwt key'
db = SQLAlchemy(app)
ma = Marshmallow(app)
jwt = JWTManager(app)

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
    username = db.Column(db.String) #should be unique
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
        'self': ma.URLFor("get_user_detail", values=dict(username="<username>")),
        "collection": ma.URLFor("get_all_users"),
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
        'self': ma.URLFor("get_recipe_detail", values=dict(recipe_name="<name>")),
        "collection": ma.URLFor("get_all_recipes"),
       }
    )

# Define the ability to serialize objects
user_schema = UserSchema()
recipe_schema = RecipeSchema()

# Define the ability to serialize a collection of objects
users_schema = UserSchema(many=True)
recipes_schema = RecipeSchema(many=True)



# Main Code
@app.route('/recipes/', methods=['GET'])
def get_all_recipes():
    """
    GET: Returns a list of all recipes 
    No authentification is required to access the recipes  
    """
    recipes = Recipe.query.all()
    return jsonify(recipes_schema.dump(recipes))

@app.route('/recipes/<string:recipe_name>', methods=['GET'])
def get_recipe_detail(recipe_name:str):
    """
    GET: Returns recipe data for the given recipe
    """
    recipe = Recipe.query.filter_by(name=recipe_name).first()
    return recipe_schema.dump(recipe)

@app.route('/recipes/', methods=['POST'])
@jwt_required()
def add_recipe():
    """
    POST: Adds a new recipe to the database
    User needs to be logged in to access this route. Furthermore the user has to be an admin
    """
    current_user = get_jwt_identity()
    user = User.query.filter_by(username=current_user).first()
    if user.is_admin:
        name = request.json.get('name')
        recipe = Recipe.query.filter_by(name=name).first()
        if recipe:
            return jsonify({"message": "Recipe already exists!"}), 409
        ingredients = request.json.get('ingredients')
        protein = request.json.get('protein')
        recipe = Recipe(name=name, ingredients=ingredients, protein=protein)
        db.session.add(recipe)
        db.session.commit()
        return jsonify({"message": "New recipe added"})
        

    return jsonify({"message": "Unauthorised"}), 403


@app.route('/recipes/<string:recipe_name>', methods=['POST'])
@jwt_required()
def put_recipe_detail(recipe_name:str):
    """
    POST: Modifies recipe data for the given recipe
    User needs to be authenticated to access this endpoint
    Furthermore the user needs to be admin
    """
    #current user is the username of the user
    current_user = get_jwt_identity()
    user = User.query.filter_by(username=current_user).first()
    if user.is_admin:
        recipe = Recipe.query.filter_by(name=recipe_name).first()
        if recipe: 
            recipe.name = request.json.get('name')
            recipe.ingredients = request.json.get('ingredients')
            recipe.protein = request.json.get('protein')
            db.session.add(recipe)
            db.session.commit()
            return jsonify({"message": "Recipe updated"})
        return jsonify({"message": "Recipe does not exist"}), 404

    return jsonify({"message": "Unauthorised"}), 403


@app.route('/recipes/<string:recipe_name>', methods=['DELETE'])
@jwt_required()
def delete_recipe_detail(recipe_name:str):
    """
    DELETE: Deletes the given 
    User needs to be authenticated to access this endpoint
    Furthermore the user needs to be admin

    """
    current_user = get_jwt_identity()
    user = User.query.filter_by(username=current_user).first()
    if user.is_admin:
        recipe = Recipe.query.filter_by(name=recipe_name).first()
        db.session.delete(recipe)
        db.session.commit()
        return jsonify({"message": "Recipe Deleted"})

    return jsonify({"message": "Unauthorised"}), 403

@app.route('/users/', methods=['GET'])
@jwt_required()
def get_all_users():
    """
    GET: Returns a list of all users
    User needs to be logged in to access this endpoint 
    Furthermore the user needs to be admin
    """
    current_user = User.query.filter_by(username=get_jwt_identity()).first()

    if current_user.is_admin:
        users_list = User.query.all()
        return jsonify(users_schema.dump(users_list))
    return jsonify({"message": "Unauthorised"}), 403

@app.route('/users/', methods=['POST'])
@jwt_required()
def add_new_user():
    """
    POST: Adds a new user to the database
    User needs to be logged in to access this endpoint 
    Furthermore the user needs to be admin
    """
    current_user = User.query.filter_by(username=get_jwt_identity()).first()
    if current_user.is_admin:
        email = request.json.get('email')
        user = User.query.filter_by(email=email).first()
        if user:
            return jsonify({"message": "Email already registered!"}), 409
        username = request.json.get('username')
        is_admin = bool(request.json.get('is_admin'))
        user = User(username=username, email=email, is_admin=is_admin)
        db.session.add(user)
        db.session.commit()
        return jsonify({"message": "New user added"})
        

    return jsonify({"message": "Unauthorised"}), 403



@app.route('/users/<string:username>', methods=['GET'])
@jwt_required()
def get_user_detail(username:str):
    """
    GET: Returns user data for the given user
    User needs to be logged in to access this endpoint
    Furthermore a user can only access their own data. Admin user can access all user data
    """
    user = User.query.filter_by(username=username).first()
    current_user = User.query.filter_by(username=get_jwt_identity()).first()
    if user:
        if current_user.username == user.username or current_user.is_admin:
            return user_schema.dump(user)
        return jsonify({"message": "Unauthorised"}), 403
    return jsonify({"message": "Bad Request"}), 400

@app.route('/users/<string:username>', methods=['POST'])
@jwt_required()
def update_user_detail(username:str):
    """
    PUT: Modifies user data for the given user

    """
    user = User.query.filter_by(username=username).first()
    current_user = User.query.filter_by(username=get_jwt_identity()).first()
    if current_user.is_admin:
        email = request.json.get('email')
        username = request.json.get('username')
        is_admin = request.json.get('is_admin')
        user = User.query.filter_by(username=username).first()
        if not user:
            return jsonify({"message": "Bad Request"}), 400
        
        user.username = username
        user.email = email
        if is_admin == "1":
            user.is_admin = True
        else:
            user.is_admin = False
        print(user.username, user.email, user.is_admin)
        db.session.add(user)
        db.session.commit()
        return jsonify({"message": "User updated"})
    return jsonify({"message": "Unauthorised"}), 403
   

@app.route('/users/<string:username>', methods=['DELETE'])
@jwt_required()
def delete_user(username:str):
    """
    DELETE: Deletes the given user
    Only admin can delete users

    """
    current_user = User.query.filter_by(username=get_jwt_identity()).first()

    if current_user.is_admin:
        user = User.query.filter_by(username=username).first()
        if user:
            db.session.delete(user)
            db.session.commit()
            return jsonify({"message": "User deleted"})
        return jsonify({"message": "Bad Request"}), 400
        print('User deleted')
    return jsonify({"message": "Unauthorised"}), 403


# Create a registration route for creating new users. If the email address is already
# registered, return 409 (conflict)
@app.route('/register', methods=['POST'])
def register():
    email = request.json.get('email')
    username = request.json.get('username')

    user = User.query.filter_by(email=email).first()
    if user:
        return jsonify({'message': 'Email address already registered!'}), 409
    new_user = User(email=email, username=username, is_admin=False)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message': 'User created successfully'}), 201 


# Create a route to authenticate your users and return JWTs. The
# create_access_token() function is used to actually generate the JWT.
# for simplicity sake users only need to provide email and username to login
@app.route("/login", methods=["POST"])
def login():
    submitted_email = request.json.get("email")
    submitted_username = request.json.get("username")
    user = User.query.filter_by(email=submitted_email).first()
    if user:
        if user.username == submitted_username:
            access_token = create_access_token(identity=submitted_username)
            return jsonify(access_token=access_token)
   
    return jsonify({"message": "Bad username or email"}), 401










if __name__ == '__main__':
    app.run()



