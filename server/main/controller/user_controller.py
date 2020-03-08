from flask import request, jsonify
from flask import current_app as app
from flask_restx import Resource

from ..util.dto import UserDto
from ..service.user_service import create_user, authenticate, get_user

api = UserDto.api
_user = UserDto.user


@api.route('')
class NewUser(Resource):
    def post(self):
        username = request.json.get('username')
        password = request.json.get('password')

        if username is None or password is None:
            api.abort(400)

        if get_user(username) is not None:
            api.abort(400)

        user = create_user(username, password)

        return jsonify({'username': user.username}, 201)


@api.route('/token')
class UserToken(Resource):
    def post(self):
        username = request.authorization['username']
        password = request.authorization['password']

        return jsonify(authenticate(username, password))