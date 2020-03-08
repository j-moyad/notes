1. Create the next folder structure

   ```
    project_folder
    │
    ├── .env
    ├── requirements.txt
    ├── manage.py
    ├── client
    ├── server
    │   ├── __init__.py
    │   ├── main
    │   │   ├──__init__.py
    │   │   ├──config.py
    │   │   ├── controller
    │   │   │   ├── __init__.py
    │   │   │   └── user_controller.py
    │   │   ├── model
    │   │   │   ├── __init__.py
    │   │   │   └── user.py
    │   │   ├── service
    │   │   │   ├── user_service.py
    │   │   │   └── __init__.py
    │   │   └── util
    │   │       ├── __init__.py
    │   │       └── dto.py   
    │   └── test
    │       └── __init__.py
    └── requirements.txt
   ```
   
2. Initialize and activate the virtualenv inside the server folder

    ```
    cd server
    python -m venv venv
    . venv/bin/activate
   ```
3. Add the dependencies

    ```
    cd ..
    nano requirements.txt
    ```

    ```
    Flask
    Flask-Cors
    Flask-Migrate
    flask-praetorian
    flask-restx
    Flask-SQLAlchemy
    Flask-Script
    python-dotenv
    psycopg2
    pytz
    sqlalchemy
    ```

    ```
    pip install -r requirements.txt
    ```

4. Add the environment variables

   ```
   nano .env
   ```
   
   ```
    SECRET_KEY=A_SECRET_KEY
    SESSION_COOKIE_NAME=my_cookie
    SQLALCHEMY_DATABASE_URI=postgresql+psycopg2://root@localhost:5432/DATABASE_NAME
    ENV=dev
    ```
   
   ```
   TIP: the SECRET_KEY can be generated with this command:
   head /dev/urandom | tr -dc A-Za-z0-9 | head -c 16 | sha256sum
   ```
   
5. Add the contents of the files defined on step 1.

    ##### manage.py

    ```
	import os
    from dotenv import load_dotenv
    import unittest
    
    from flask_praetorian import Praetorian
    from flask_migrate import Migrate, MigrateCommand
    from flask_script import Manager
    
    from server.main import create_app, db
    from server.main.model import user
    from server import blueprint
    basedir = os.path.abspath(os.path.dirname(__file__))
    load_dotenv(os.path.join(basedir, '.env'))
    
    app = create_app(os.environ.get('ENV') or 'dev')
    app.register_blueprint(blueprint)
    
    app.app_context().push()
    
    manager = Manager(app)
    migrate = Migrate(app, db)
    guard = Praetorian()
    
    manager.add_command('db', MigrateCommand)
    
    guard.init_app(app, user.User)
    
    
    @manager.command
    def run():
        app.run(host='0.0.0.0')
    
    
    @manager.command
    def test():
        """Runs the unit tests."""
        tests = unittest.TestLoader().discover('app/test', pattern='test*.py')
        result = unittest.TextTestRunner(verbosity=2).run(tests)
        if result.wasSuccessful():
            return 0
        return 1
    
    
    if __name__ == '__main__':
        manager.run()

    ```

    ##### server/__init__.py

    ```
    from flask_restx import Api
    from flask import Blueprint
    
    from .main.controller.user_controller import api as user_ns
    
    blueprint = Blueprint('api', __name__)
    
    api = Api(blueprint,
              title='FLASK RESTPLUS API BOILER-PLATE WITH JWT',
              version='1.0',
              description='a boilerplate for flask restplus web service'
              )
    
    api.add_namespace(user_ns, path='/user')

    ```
   
    ##### server/main/__init__.py

    ```
    from flask import Flask
    from flask_sqlalchemy import SQLAlchemy
    from flask_migrate import Migrate
    from flask_cors import CORS
    from .config import config_by_name
    
    db = SQLAlchemy()
    cors = CORS()
    migrate = Migrate()
    
    
    def create_app(config_name):
        app = Flask(__name__)
        app.config.from_object(config_by_name[config_name])
        db.init_app(app)
        cors.init_app(app)
    
        return app

    ```
   
    ##### server/main/config.py

    ```
    import os
    from dotenv import load_dotenv
    
    # basedir = os.path.abspath(os.path.dirname(__file__))
    basedir = os.path.abspath(os.getcwd())
    load_dotenv(os.path.join(basedir, '.env'))
    
    
    class Config:
        # General
        print(basedir)
        SECRET_KEY = os.environ.get('SECRET_KEY')
    
        # Database
        SQLALCHEMY_DATABASE_URI = os.environ.get("SQLALCHEMY_DATABASE_URI")
        SQLALCHEMY_TRACK_MODIFICATIONS = True
        SQLALCHEMY_ECHO = True
    
        # JWT
        JWT_ACCESS_LIFESPAN = {'hours': 24}
        JWT_REFRESH_LIFESPAN = {'days': 30}
    
    
    class DevelopmentConfig(Config):
        DEBUG = True
        SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    
    class TestingConfig(Config):
        DEBUG = True
        TESTING = True
        PRESERVE_CONTEXT_ON_EXCEPTION = False
        SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    
    class ProductionConfig(Config):
        DEBUG = False
        # uncomment the line below to use postgres
        # SQLALCHEMY_DATABASE_URI = postgres_local_base
    
    
    config_by_name = dict(
        dev=DevelopmentConfig,
        test=TestingConfig,
        prod=ProductionConfig
    )
    
    key = Config.SECRET_KEY

    ```
   
   ##### server/main/controller/user_controller.py
   
    ```
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
    ```
   
    ##### server/main/model/user.py
   
    ```
    from .. import db

    
    class User(db.Model):
        __tablename__ = 'user'
    
        id = db.Column(db.Integer, primary_key=True)
        username = db.Column(db.String(), index=True)
        password = db.Column(db.String())
        roles = db.Column(db.Text)
        is_active = db.Column(db.Boolean, default=True, server_default='true')
    
        @property
        def rolenames(self):
            try:
                return self.roles.split(',')
            except Exception:
                return []
    
        @classmethod
        def lookup(cls, username):
            return cls.query.filter_by(username=username).one_or_none()
    
        @classmethod
        def identify(cls, id):
            return cls.query.get(id)
    
        @property
        def identity(self):
            return self.id
    
        def is_valid(self):
            return self.is_active

    ```   
   
    ##### server/main/service/user_service.py
   
    ```
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

    ```   

    ##### server/main/util/dto.py
   
    ```
    from flask_restx import Namespace, fields
    
    
    class UserDto:
        api = Namespace('user', description='user related operations')
        user = api.model('user', {
            'username': fields.String(required=True, description='user username'),
            'password': fields.String(required=True, description='user password'),
            'id': fields.String(description='user Identifier')
        })

    ```
6.  Initialize the database and create the first migration

    ```
    python manage.py db init
    python manage.py db migrate -m 'Initial migration'
    python manage.py db upgrade
    ```
    
    ```
    NOTE: Whenever the database model changes, the steps of migrate and upgrade must have to be ran again.
    
    NOTE 2: The migration command does not normally updates the column definition when the length is changed.
    To remedy this, add "compare_type=True" in the context.configure() inside of the methods run_migrations_offline()
    and run_migrations_online() of the file migrations/env.py 
    ```

##### Sources:
```
https://www.freecodecamp.org/news/structuring-a-flask-restplus-web-service-for-production-builds-c2ec676de563/
http://blog.code4hire.com/2017/06/setting-up-alembic-to-detect-the-column-length-change/
```