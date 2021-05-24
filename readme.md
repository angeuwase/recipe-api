# RECIPE API

A restful API developed using flask  

## Features
An API that allows users to view all the recipes stored in a database.  
No authentification is needed to view recipes   
Users need to be logged in to access and update their user data  
Only admin user can add new recipes/ update existing recipes/ delete recipes/ delete users   
Users are authenticated using JWT


## Libraries
Flask-Marshmallow : Serialization and Deserialization   
Flask-SQLAlchemy : Database ORM   
Flask-JWT-Extended: User authentification using JWT   


<hr>

# Design

1. Identify Participants
Users   
-active users. external to the organisation. will be consuming the API

2. Identify the activities
find a recipe  

3. Break the activities into steps   
Step 1: Register for an account   
Step 2: Get a list of all recipes   
Step 3: Request desired recipe   

4. Create API definition (ID the resources, the actions you want to perform on them, and the HTTP methods that support those actions)  
/users/                     GET     returns a list of all registered users   
/users/                     POST    adds a new user 
/users/<int:id>             GET     returns the user data for the user with the given ID
/users/<int:id>             PUT     modifies the user data for the user with the given ID
/users/<int:id>             DELETE  deletes the user with the given ID
/recipes/                   GET     returns a list of all recipes stored in the database
/recipes/                   POST    adds a new recipe
/recipes/<int:id>           GET     returns the recipe data for the recipe with the given ID
/recipes/<int:id>           PUT     modifies the recipe data for the recipe with the given ID
/recipes/<int:id>           DELETE  deletes the recipe with the given ID


To perform POST, PUT and DELETE requests a user needs to be logged in.  
