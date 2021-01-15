import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from src.database.models import db_drop_and_create_all, setup_db, Drink
from src.auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
'''
#db_drop_and_create_all()

## ROUTES
'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks')

def getdrinks():
    drinks=[drink.short() for drink in Drink.query.all()]
    return jsonify( {"success": True, "drinks": drinks})

'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks-detail')
@requires_auth('get:drinks-detail')
def getdrinksdetails(payload):
    drinks=[drink.long() for drink in Drink.query.all()]
    return jsonify( {"success": True, "drinks": drinks})


'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks',methods=['POST'])
@requires_auth('post:drinks')
def postdrinks(payload):
    body = request.get_json()
    try:
        drink=Drink(title=body.get("title"),recipe=json.dumps(body.get("recipe")))
        drink.insert()
    except Exception as e:
        print(e)
        abort(422)
    return jsonify( {"success": True, "drinks": drink.long()})


'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<id>',methods=['PATCH'])
@requires_auth('patch:drinks')
def editdrinks(payload,id):
    body = request.get_json()
    drink=Drink.query.get(id)
    if not drink:
        abort(404)
    if body:
        title=body.get("title",None)
        recipe=body.get("recipe",None)
        try:    
            if title:
                drink.title=title
            elif recipe:
                drink.reciepe=json.dumps(recipe)
            drink.update()
        except Exception as e:
            print(e)
            abort(422)

    return jsonify( {"success": True, "drinks": [drink.long() for drink in Drink.query.all()]})


'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<id>',methods=['DELETE'])
@requires_auth('delete:drinks')
def deletedrinks(payload,id):
    drink=Drink.query.get(id)
    try:
        if not drink:
            abort(404)
        drink.delete()
    except:
        abort(422)

    return jsonify( {"success": True, "delete": id})

## Error Handling
'''
Example error handling for unprocessable entity
'''
@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
                    "success": False, 
                    "error": 422,
                    "message": "unprocessable"
                    }), 422

'''
@TODO implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False, 
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''

'''
@TODO implement error handler for 404
    error handler should conform to general task above 
'''
@app.errorhandler(404)
def not_found(error):
    return jsonify({'success':False,'message':'Resource not found','error':404}),404

'''
@TODO implement error handler for AuthError
    error handler should conform to general task above 
'''
@app.errorhandler(AuthError)
def handle_auth_error(ex):
    response = jsonify({
        "success": False,
        "error": ex.status_code,
        "message":ex.error}),ex.status_code
    return response