from application.delete_file import delete_file
from flask_restful import Resource, reqparse, request
from werkzeug.datastructures import FileStorage
from flask_jwt_extended import jwt_required, get_jwt_identity, current_user, get_jwt
from signup import getOTP
from sqlalchemy import and_
from instances import db, app
from application.models import User, user_schema, Creator, creator_schema
import os
import uuid


class CreatorResource(Resource):

    @jwt_required()
    def post(self):
        image = request.files.get('image')
        artist_name = request.form.get('artist')
        id = get_jwt_identity()
        user = current_user()
        creator = Creator.query.filter(Creator.id == id).first()
        artist = Creator.query.filter(Creator.artist == artist_name).first()
        if creator:
            return {"message": "creator already exists"}, 400
        if artist:
            return {"message": "artist name already exists try using another name"}, 400

        creator = Creator(id=id, artist=artist_name, disabled=False)

        if not image or image.filename == '':
            image_filename = None
        else:
            image_filename = 'a' + str(uuid.uuid4()) + \
                '.' + image.filename.split('.')[-1]
        if image_filename:
            image.save(os.path.join(
                app.config['IMAGE_FOLDER'], image_filename))
            creator.image = image_filename
        user.user_type = "CREATOR"
        db.session.add_all([creator, user])
        db.session.commit()
        return {"message": "success", "creator": creator_schema.dump(creator)}

    @jwt_required()
    def get(self):
        user_id = get_jwt_identity()
        return {"user": user_schema.dump(User.query.get_or_404(user_id))}

    @jwt_required()
    def put(self):
        if get_jwt()['user_type'] == 'ADMIN':
            creator_id = request.form.get("creator_id")
            disabled = True if request.form.get(
                "disabled") == 'true' else False
            policy_violate = request.form.get("policy_violate")

            creator = Creator.query.get_or_404(creator_id)
            creator.disabled = disabled
            creator.policy_violate = policy_violate
            db.session.add(creator)
            db.session.commit()
            return {"message": "success", "creator": creator_schema.dump(creator)}

        if get_jwt()['user_type'] == 'CREATOR':
            creator = Creator.query.get_or_404(get_jwt_identity())

            image = request.files.get('image')
            artist_name = request.form.get('artist')

            crt = Creator.query.filter(and_(Creator.id != creator.id,
                                            Creator.artist == artist_name)).first()

            if crt:
                return {"message": "artist name already exists try using different name"}
            image = request.files['image']

            empty = [None, '', ' ']

            if artist_name not in empty:
                creator.artist = artist_name

            if image.filename == '':
                image_filename = None
            else:
                if creator.image:
                    delete_file(os.path.join(
                        app.config['IMAGE_FOLDER'], creator.image))

                image_filename = 'a' + \
                    str(uuid.uuid4()) + '.' + image.filename.split('.')[-1]

                if image_filename:
                    image.save(os.path.join(
                        app.config['IMAGE_FOLDER'], image_filename))

                creator.image = image_filename

            db.session.add(creator)
            db.session.commit()

        return {"message": "unauthorized"}, 403
