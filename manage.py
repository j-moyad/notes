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
