from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_caching import Cache
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_marshmallow import Marshmallow
from celery import Task, Celery
import redis
from config import config_object as config
from dotenv import load_dotenv


load_dotenv()

cache = Cache()
app = Flask(__name__)
CORS(app)
jwt = JWTManager(app)
db = SQLAlchemy()
ma = Marshmallow(app)
redisInstance = redis.Redis(
    host=config['CACHE_REDIS_HOST'], port=config['CACHE_REDIS_PORT'])


def celery_init_app(app):
    class FlaskTask(Task):
        def call(self, *args: object, **kwargs: object) -> object:
            with app.app_context():
                return self.run(*args, **kwargs)

    celery_app_init = Celery(app.name, task_cls=FlaskTask)
    celery_app_init.config_from_object(config["CELERY"])
    celery_app_init.set_default()
    app.extensions["celery"] = celery_app_init
    return celery_app_init


celery_app = celery_init_app(app)
celery_app.conf.timezone = 'Asia/Kolkata'
