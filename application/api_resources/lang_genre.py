from flask_restful import Resource, request
from application.models import Genre, Language, many_language_schema, many_genre_schema
from flask_jwt_extended import jwt_required, get_jwt
from instances import db, cache
from application.contollers import user

class GenreResource(Resource):
    @cache.cached(timeout=300)
    def get(self):
        genres = Genre.query.all()
        return {"genres": many_genre_schema.dump(genres)}

    @jwt_required()
    def post(self):
        if get_jwt()['user_type'] != 'ADMIN':
            return {"message": "unauthorized"}, 401

        reqname = request.form.get('name').strip()
        genre_get = Genre.query.filter(Genre.name.ilike(reqname)).first()

        if reqname == '' or reqname == None or genre_get:
            return {"message": "conflict"}, 409

        genre = Genre(name=reqname)
        db.session.add(genre)
        db.session.commit()

        return {"message": "success"}


class LanguageResource(Resource):
    @cache.cached(timeout=300)
    def get(self):
        languages = Language.query.all()
        return {"languages": many_language_schema.dump(languages)}

    @jwt_required()
    def post(self):
        if get_jwt()['user_type'] != 'ADMIN':
            return {"message": "unauthorized"}, 401

        reqname = request.form.get('name').strip()
        language_get = Language.query.filter(
            Language.name.ilike(reqname)).first()

        if reqname == '' or reqname == None or language_get:
            return {"message": "conflict"}, 409

        language = Language(name=reqname)
        db.session.add(language)
        db.session.commit()

        return {"message": "success"}
