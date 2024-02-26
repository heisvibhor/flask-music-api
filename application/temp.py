from celery import Task, Celery
from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, current_user
from flask_restful import Resource, Api
from werkzeug.security import generate_password_hash, check_password_hash

from models import User, db, Song

app = Flask(name)

app.config["JWT_SECRET_KEY"] = "super-secret-by-Vibhor"
jwt = JWTManager(app)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///proj.sqlite3"
db.init_app(app)


@jwt.user_lookup_loader
def user_lookup_callback(_jwt_header, jwt_data):
    identity = jwt_data["sub"]
    return User.query.filter_by(id=identity).one_or_none()


# celery

app.config.from_mapping(
    CELERY=dict(
        broker_url="redis://localhost",
        result_backend="redis://localhost",
        task_ignore_result=True,
    ),
)


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

api = Api(app)


class HelloWorld(Resource):
    def get(self):
        return {'hello': 'world'}


api.add_resource(HelloWorld, '/')


class LoginVibhorify(Resource):
    def post(self):
        email = request.json.get("email", None)
        password = request.json.get("password", None)
        if not email or not password:
            return {"msg": "Missing username or password"}, 400

        user: User = User.query.filter_by(email=email, password=password).first()
        if not user:
            return {"msg": "Invalid email or password"}, 401

        access_token = create_access_token(identity=user.id, additional_claims={"user_type": user.user_type})

        return {"access_token": access_token}, 200


api.add_resource(LoginVibhorify, '/login')


class SongResource(Resource):

    @jwt_required()
    def get(self, song_id=None):
        print(current_user.user_type)
        if song_id:
            song = Song.query.filter_by(id=song_id).first()
            if not song:
                return {"msg": "Song not found"}, 404
            return {"data": song}
        else:
            songs_query = Song.query

            if 'language' in request.args:
                songs_query = songs_query.filter_by(language=request.args.get('language'))

            if 'genre' in request.args:
                songs_query = songs_query.filter_by(genre=request.args.get('genre'))

            return {"data": jsonify(songs_query.all())}


api.add_resource(SongResource, '/song', '/song/<int:song_id>')