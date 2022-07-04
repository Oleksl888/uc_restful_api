# Ultimate CookBook RESTFul API
## A [Cookbook Api](https://ucookbook-api.herokuapp.com) that can be used with any client. Wrapped with Swagger UI for your convenience

## How it works
The application is based on Flask framework with SQLAlchemy and SQLite3 or Postgres database.

Cook Book Database contains over 100 recipes. Requests must contain valid JSON.

The following endpoints are supported with following methods:

1. **/recipes** OR **/recipes/{id}**
   - GET: Returns recipes. No user authorization/authentication required. Request may return a specified recipe by id. If id is omitted, all entries will be returned. 
   
     Request example:
     > curl -X GET https://ucookbook-api.herokuapp.com/recipes -H accept: application/json 

     Response Example:
     > {
  "name": "string",
  "recipe": "string",
  "feedback": [
    {
      "name": "string",
      "message": "string"
    }
  ],
  "ingredients": [
    "string"
  ]
}
    
   - POST: Creates a recipe. Basic user authentication required. Request must be a valid JSON and contain mandatory fields **name** and **recipe**. Ingredients field is optional. URL must not contain {id}.
   
     Request example:
     > curl -X 'POST' \
  'https://ucookbook-api.herokuapp.com/recipes' \
  -H 'accept: */*' \
  -H 'Authorization: Bearer *YOUR JWT TOKEN HERE*' \
  -H 'Content-Type: application/json' \
  -d '{
  "name": "string",
  "recipe": "string"
}' 

     Successful Response Example:
     > Code 201, {'message': 'Recipe has been added'}

   - PUT: Updates a selected recipe. Basic user authentication required. Request must be a valid JSON and contain mandatory fields **name** and **recipe**. Ingredients field is optional. URL must contain {id}.
   
     Request example:
     >    curl -X 'PUT' \
  'https://ucookbook-api.herokuapp.com/recipes/1' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer *YOUR JWT TOKEN HERE*' \
  -H 'Content-Type: application/json' \
  -d '{
  "name": "string",
  "recipe": "string",
}'

     Successful Response Example:
     >Code 201, {'message': 'Recipe has been updated'}

   - PATCH: Partially updates a selected recipe. Basic user authentication required. Request must be a valid JSON. URL must contain {id}.
   
     Request example:
      >curl -X 'PATCH' \
  'https://ucookbook-api.herokuapp.com/recipes/1' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer *YOUR JWT TOKEN HERE*' \
  -H 'Content-Type: application/json' \
  -d '{
  "name": "string",
  "recipe": "string",
}'

     Successful Response Example:
     >Code 201, {'message': 'Recipe has been updated'}

   - DELETE: Deletes a selected recipe. Basic user authentication required. Request must be a valid JSON. URL must contain {id}.
   
     Request example:
      >curl -X 'DELETE' \
  'https://ucookbook-api.herokuapp.com/recipes/1' \
  -H 'accept: */*' \
  -H 'Authorization: Bearer *YOUR JWT TOKEN HERE*'

     Successful Response Example:
     >Code 204, ""


2. **/ingredients** OR **/ingredients/{id}**
   - GET: Returns ingredients. No user authorization/authentication required. Request may return a specified ingredient by id. If id is omitted, all entries will be returned. 
   - POST: Creates an ingredient. Basic user authentication required. Request must be a valid JSON and contain mandatory fields **name**. Recipes field is optional. URL must not contain {id}.
   - PUT: Updates a selected ingredient. Basic user authentication required. Request must be a valid JSON and contain mandatory fields **name**. Recipes field is optional. URL must contain {id}.
   - PATCH: Partially updates a selected ingredient. Basic user authentication required. Request must be a valid JSON. URL must contain {id}.
   - DELETE: Deletes a selected ingredient. Basic user authentication required. Request must be a valid JSON. URL must contain {id}.


3. **/feedback** OR **/feedback/{id}**
   - GET: Returns only anonymous feedback that is not linked to any user or recipe. No user authorization/authentication required. Request may return a specified feedback by id. If id is omitted, all entries will be returned. 
   - POST: Creates feedback entry. Basic user authentication required. Request must be a valid JSON and contain mandatory fields **name**, **message**. If user_id or recipe_id is in request feedback message is being linked to that user_id or recipe_id. If those are not found feedback is added anonymously not specifying any recipe or user.
     URL must not contain {id}.
   - PUT: Updates a selected feedback entry. Basic user authentication required. Request must be a valid JSON and contain mandatory fields **name**, **message**. Put methods will change only message but will not alter message ownership to recipe and user. URL must contain {id}.
   - PATCH: Partially updates a selected feedback entry. Basic user authentication required. Request must be a valid JSON. Patch methods will change only message but will not alter message ownership to recipe and user. URL must contain {id}.
   - DELETE: Deletes a selected feedback entry. Basic user authentication required. Request must be a valid JSON. URL must contain {id}.


4. **/tracker**
   - GET: Shows info on client's activity. No user authorization/authentication required. 


5. **/register** 
   - POST: Creates new user if provided unique name and email. No user authorization/authentication required. Request must be a valid JSON and contain mandatory fields **name**, **email**, **password**. Name must be only alphabetic and password must contain at least 8 symbols. Confirmation email is being sent upon successful registration. Basic user privileges will be set with this endpoint.


6. **/login** 
   - POST: Authenticates user and returns a JWT token in response body. Request must be a valid JSON and contain mandatory fields **name**, **password**. Upon successful login a jwt token is issued with expiration for 2 hours. JWT token contains user id and its authorization level.


7. **/users** OR **/users/{uuid}**
   - GET: Returns users list. Admin authorization required. Request may return a specified feedback by uuid. If id is omitted, all entries will be returned. 
   - POST: Creates new user from admin panel. Admin authorization required. Request must be a valid JSON and contain mandatory fields **name**, **email**, **password**. Name must be only alphabetic and password must contain at least 8 symbols. URL must not contain {uuid}.
     URL must not contain {id}.
   - PUT: Updates a selected user from admin panel. Admin authorization required. Request must be a valid JSON and contain mandatory fields **name**, **email**, **password**. Name must be only alphabetic and password must contain at least 8 symbols. Optionally admin can alter other fields in user account such as st admin privileges. URL must contain {uuid}.
   - PATCH: Partially updates a selected user from admin panel. Admin authorization required. Request must be a valid JSON. Name must be only alphabetic and password must contain at least 8 symbols. Optionally admin can alter other fields in user account such as st admin privileges. URL must contain {uuid}.
   - DELETE: Deletes a selected user. Admin authorization required. Request must be a valid JSON. URL must contain {uuid}.

8. **/search**
   - GET: Returns recipes list. No user authorization/authentication required. Look for a recipe by name and it will return a list of matches. If you look up a recipe by ingredients, make sure you add commas between words otherwise it won't produce the correct result. Params to include are 'recipe' and 'ingredient'.

## Enjoy and have fun
