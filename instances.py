from flask import Flask
from flask_sqlalchemy import SQLAlchemy 
from flask_caching import Cache
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_marshmallow import Marshmallow
from celery import Task, Celery

cache = Cache()
app = Flask(__name__)
CORS(app)
jwt = JWTManager(app)
db = SQLAlchemy()
ma = Marshmallow(app)
def celery_init_app(app):
    class FlaskTask(Task):
        def call(self, *args: object, **kwargs: object) -> object:
            with app.app_context():
                return self.run(*args, **kwargs)

    celery_app_init = Celery(app.name, task_cls=FlaskTask)
    celery_app_init.config_from_object(app.config["CELERY"])
    celery_app_init.set_default()
    
    return celery_app_init
