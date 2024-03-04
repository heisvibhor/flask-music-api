from instances import db, app, cache
import os
from dotenv import load_dotenv
from config import config_object
from celery import Task, Celery

load_dotenv()

with app.app_context():
    app.config.from_mapping(config_object)
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
    db.init_app(app)
    cache.init_app(app)

app.app_context().push()
def celery_init_app(app):
    class FlaskTask(Task):
        def call(self, *args: object, **kwargs: object) -> object:
            with app.app_context():
                return self.run(*args, **kwargs)

    celery_app_init = Celery(app.name, task_cls=FlaskTask)
    celery_app_init.config_from_object(app.config["CELERY"])
    celery_app_init.set_default()
    app.extensions["celery"] = celery_app_init
    return celery_app_init

celery_app = celery_init_app(app)

from application.login import *
from application.api import *
from application.signup import *


if __name__ == '__main__':
    app.run(host='0.0.0.0', port ="5001", debug=True, threaded = False)