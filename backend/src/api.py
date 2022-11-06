import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink, db
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@TODO uncomment the following line to initialize the database
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
!! Running this function will add one
'''
# db_drop_and_create_all()

# ROUTES
'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks', methods=['GET'])
def get_drinks():
    selection = Drink.query.all()

    return jsonify({
        'success': True,
        "drinks": [
            drinks.short() for drinks in selection
        ]
    }), 200


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
def get_drinks_detail(payload):
    selection = Drink.query.all()

    return jsonify({
        'success': True,
        "drinks": [
            drinks.long() for drinks in selection
        ]
    }), 200


'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} 
    where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def post_drinks(payload):
    if request.method == "POST":
        body = request.get_json()
        # print(body) # debugger
        try:
            recipe = body['recipe']
            if type(recipe) is dict:
                recipe = [recipe]

            title = body['title']
            drink = Drink(
                title=title,
                recipe=json.dumps(recipe)
            )
            drink.insert()
            drinks = [drink.long()]

            return jsonify({
                'success': True,
                'drinks': drinks
            })
        except():
            abort(400)


'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} 
    where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks/<int:drink_id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def edit_drink(payload, drink_id):
    body = request.get_json()

    selection = db.session.query(Drink).filter(Drink.id == drink_id).one_or_none()

    if selection is None:
        abort(404)

    new_title = body.get('title')
    new_recipe = body.get('recipe')

    if (new_title, new_recipe) is None:
        abort(422)

    try:
        selection.title = new_title
        selection.update()

        return jsonify({
            'success': True,
            "drinks": [selection.long()]
        }), 200

    except():
        abort(422)


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


@app.route('/drinks/<int:drink_id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(payload, drink_id):

    drink = db.session.query(Drink).filter(Drink.id == drink_id).one_or_none()
    # print(drink) # debugger

    if drink is None:
        abort(404)

    # print(drink) # debugger

    try:
        drink.delete()

        return jsonify({
            'success': True,
            'delete': drink_id
        }), 200

    except():
        abort(404)


# Error Handling
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
    each error handler should return (with appropriate messages):
             jsonify({
                    "success": False,
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''


@app.errorhandler(400)
def internal_server_error(error):
    return jsonify({
        "success": False,
        "error": 400,
        "message": "Bad Request"
    }), 400


@app.errorhandler(401)
def unauthorized(error):
    return jsonify({
        "success": False,
        "error": 401,
        "message": "unauthorized"
    }), 401


@app.errorhandler(403)
def permission_error(error):
    return jsonify({
        "success": False,
        "error": 403,
        "message": "You do not have proper authorization"
    }), 403


'''
@TODO implement error handler for 404
    error handler should conform to general task above
'''


@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "resource not found"
    }), 404


@app.errorhandler(405)
def Method_not_allowed(error):
    return jsonify({
        "success": False,
        "error": 405,
        "message": "Method not allowed"
    }), 405


@app.errorhandler(500)
def internal_server_error(error):
    return jsonify({
        "success": False,
        "error": 500,
        "message": "internal server error"
    }), 500


'''
@TODO implement error handler for AuthError
    error handler should conform to general task above
'''


@app.errorhandler(AuthError)
def authError(error):
    return jsonify({
        "success": False,
        "error": error.status_code,
        "message": error.error['description'],
    }), error.status_code
