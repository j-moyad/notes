from server.main import db
from server.main.model.user import User
from flask import current_app as app


def create_user(username, password, roles=[]):
    guard = app.extensions['praetorian']
    user = User(username=username, password=guard.hash_password(password), roles=''.join(roles))

    db.session.add(user)
    db.session.commit()

    return user


def authenticate(username, password):
    guard = app.extensions['praetorian']

    user = guard.authenticate(username, password)

    return {'token': guard.encode_jwt_token(user)}


def get_user(username):
    return User.query.filter_by(username=username).first()
