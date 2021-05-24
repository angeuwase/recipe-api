# Notes


This is a rest API  
It allows registered users to be able to programmatically access recipe information from the application   
Users can only access recipe data   
Admin user can access and modify recipe and user data   


<hr>

# Handling parameters passed in a request message

-parameters are accessed via `request.args.get()`  

Request message:   
```
GET http://localhost:5000/name?username=ange
```

View function:
```

@app.route('/name')
def name():
    username = request.args.get('username')
    return jsonify(message=f'your name is {username}')


```

<hr>


# Seeding database with flask CLI
1. write the function, turn the function into a command by giving it the cli decorator. the argument is the command that will be used to call the function   
```
# Flask CLI 
@app.cli.command('create_database')
def create_database():
    db.create_all()

    print('Database tables created')

@app.cli.command('seed_db')
    user1 = User(email='admin@gmail.com', username='adminuser')
    user2 = User(email='testuser@gmail.com', username='testuser')
    recipe1 = Recipe(name='Roast Chicken', protein='chicken', ingredients='chicken, onions, carrots, celery, garlic, oil, lemon, fresh herbs')
    recipe2 = Recipe(name='Creamy Beef Pasta', protein='beef', ingredients='beef, garlic, basil, oregano, salt, pepper, flour, tomato sauce, beef broth, pasta, heavy cream, cheddar cheese')
    db.session.add_all([user1, user2, recipe1, recipe2])
    db.session.commit()
    print('Database seeded')

@app.cli.command('destroy_database')
def destroy_databse():
    db.drop_all()
    print('Database tables destroyed')
```
2. to run the command, in the terminal type `flask <command>` 
```
$ flask create_database
$ flask seed_db
```

3. Open up SQLite database using DB Browser for SQLite and you will see the database has been populated   


<hr>


# Returning database query results as json

jsonify() can take a python dictionary and convert it to json data   

To send/ receive a representation of a web resource stored in a database, you need to do serialization and deserialization.   

Serialization: Serialization is a process of converting an Object into stream of bytes so that it can be transferred over a network or stored in a persistent storage (database/ file/ etc). When it comes to web APIs, serialization is done to take a database query result and convert it to a stream of bytes that can be transferred over the network to the client in json format.    
Deserialization: the opposite of serialization.   

For serialization/deserializationn: use flask-marshmallow   
https://flask-marshmallow.readthedocs.io/en/latest/   

```
pip install flask-marshmallow marshmallow-sqlalchemy

from flask_marshmallow import Marshmallow

ma = Marshmallow(app)

```

1. Write your sqlalchemy models  
```
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
```

2. Define your output format with marshmallow by defining the marshmallow schemas for each model
```
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

```
3. Output the data in the view functions using the `dumps()` method of the schema objects  
-for multiple items the output is a list, that you need to jsonify.  
```
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

```

<hr>

# API Security 

-Using flask-jwt-extended for authenficiation using JWT   

## Installation 
```
$ pip install flask-jwt-extended
```

## Configuration  
You need to specify JWT_SECRET_KEY   

```
from flask_jwt_extended import JWTManager, create_access_token, get_jwt_identity, jwt_required

app.config['JWT_SECRET_KEY'] = 'super jwt key'
jwt = JWTManager(app)
```

## Usage   

1. Create a login route for users to login. When a user is successfully authenticated, they are logged in and issued a JWT using `create_access_token()`   
```

```

2. Any routes that require authentification should be protected using `jwt_required()`. You can find out the user of the jwt token by calling `current_user = get_jwt_identity()`
```

```

3. To access a jwt_required protected view you need to send in the JWT with each request. By default, this is done with an authorization header that looks like:

`Authorization: Bearer <access_token>`

To get the JWT you first need to log in




