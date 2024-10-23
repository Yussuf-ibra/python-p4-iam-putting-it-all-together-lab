#!/usr/bin/env python3

from flask import request, session, make_response
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError

from config import app, db, api
from models import User, Recipe

class Signup(Resource):
    def post(self):
        data = request.get_json()
        user = User(username = data['username'],
                    image_url = data['image_url'],
                    bio = data['bio']
                    )
        user.password_hash = data['password']
        db.session.add(user)
        db.session.commit()
        if user:
            session['user_id'] = user.id
            response = user.to_dict(only=('id', 'username', 'image_url', 'bio'))
            return make_response(response, 201)
        else:
            return make_response({'error': 'Failed to create user'}, 422)
        

class CheckSession(Resource):
    def get(self):
        user_id = session['user_id']
        if user_id:
            user = User.query.filter_by(id = user_id).first()
            response = user.to_dict(only=('id', 'username', 'image_url', 'bio'))
            return make_response(response, 200)
        else:
            return make_response({
                "message": "User was not found"
            }, 401)

class Login(Resource):
    def post(self):
        username = request.get_json()['username']
        user = User.query.filter(User.username == username).first()

        password = request.get_json()['password']
        if user.authenticate(password):
            session['user_id'] = user.id
            return make_response(user.to_dict(), 200)
        else:
            return make_response({
                'error', 'Invalid username or password'
            }, 401)
            

class Logout(Resource):
    def delete(self):
        if session['user_id']:
            session['user_id'] = None
            return make_response({}, 204)
        else:
            return make_response({
                "message": "You are not logged in"
            }, 401)

class RecipeIndex(Resource):
    def get(self):
        if not session['user_id']:
           return make_response({
               "message": 'You are not logged in'
           }, 401)
        response = [recipe.to_dict() for recipe in Recipe.query.all()]
        return make_response(response, 200)
    
    def post(self):
        if not session['user_id']:
            return make_response({
                "message":"You have not logged in"
            }, 401)
        data = request.get_json()
        recipe = Recipe(
            title = data['title'],
            instructions = data['instructions'],
            minutes_to_complete = data['minutes_to_complete'],
            user_id = session['user_id']
        )

        db.session.add(recipe)
        db.session.commit()

        if recipe:
            response = recipe.to_dict()
            return make_response(response, 201)
        else:
            return make_response({
                "message": "Recipe was not created"
            }, 422)

api.add_resource(Signup, '/signup', endpoint='signup')
api.add_resource(CheckSession, '/check_session', endpoint='check_session')
api.add_resource(Login, '/login', endpoint='login')
api.add_resource(Logout, '/logout', endpoint='logout')
api.add_resource(RecipeIndex, '/recipes', endpoint='recipes')


if __name__ == '__main__':
    app.run(port=5555, debug=True)