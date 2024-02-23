from instances import db, app, cache
import os
from dotenv import load_dotenv
from config import config_object

load_dotenv()

with app.app_context():
    app.config.from_mapping(config_object)
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
    db.init_app(app)
    cache.init_app(app)

app.app_context().push()


from application.login import *
from application.api import *
from application.signup import *


if __name__ == '__main__':
    app.run(host='::', port ="5001", debug=True, threaded = False)