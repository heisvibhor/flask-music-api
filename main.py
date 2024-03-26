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

from application.tasks import *
from application.contollers import *
from application.signup import *
from application.api import *
from application.login import *
from instances import celery_app
from application.tasks import *

# celery -A main.celery_app beat
# celery -A main.celery_app worker

if __name__ == '__main__':
    app.run(host='0.0.0.0', port="5001", debug=True, threaded=False)
