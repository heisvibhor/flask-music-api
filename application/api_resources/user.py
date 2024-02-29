from application.delete_file import delete_file
from werkzeug.security import generate_password_hash
from flask_restful import Resource, reqparse, request
from werkzeug.exceptions import BadRequest
from werkzeug.datastructures import FileStorage
from flask import jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from application.signup import getOTP
from instances import db, app
from application.models import User, user_schema
import os
import uuid

class UserResource(Resource):
    signup_parser = reqparse.RequestParser()
    signup_parser.add_argument('username', type=str, required=True, location=["form"])
    signup_parser.add_argument('password', required=True, location=["form"])
    signup_parser.add_argument('email', required=True, location=["form"])
    signup_parser.add_argument('name', required=True, location=["form"])
    signup_parser.add_argument('language', required=True, location=["form"])
    signup_parser.add_argument('image', type=FileStorage, location=['files'])

    def post(self):
        args = self.signup_parser.parse_args()
        password = args.get('password')
        email = args.get('email')
        name = args.get('name')
        language = args.get('language')
        image = args.get('image')   

        if not image or image.filename == '':
            image_filename = None
        else:
            image_filename = 'a' + str(uuid.uuid4()) + \
                '.' + image.filename.split('.')[-1]
        if image_filename:
            image.save(os.path.join(app.config['IMAGE_FOLDER'], image_filename))

        empty = [None, '']

        if email in empty or password in empty or name in empty or language in empty:
            return jsonify({"message": "invalid input"}), 406

        user = User.query.where(User.email == email).first()

        if user:
            return jsonify({"message": "email already exists"}), 406
        else:
            user = User(username=email, password=generate_password_hash(
                password), email=email, name=name, language=language, image=image_filename)
            db.session.add(user)
            db.session.commit()
            return jsonify({
                'token': create_access_token(identity=user.id, additional_claims={"user_type": user.user_type}),
                'user_id': user.id,
                'user_type': user.user_type,
                'email': user.email,
                'message': 'success'
            }), 200

    @jwt_required()   
    def get(self):
        user_id = get_jwt_identity()
        return {"user": user_schema.dump(User.query.get_or_404(user_id))}
    
    @jwt_required()   
    def put(self):
        user_id = get_jwt_identity()
        user = User.query.get_or_404(user_id)

        name = request.form.get('name')
        language = request.form.get('language')
        image = request.files['image']

        empty = [None, '', ' ']

        if image.filename=='':
            image_filename =  None
        else:
            if user.image:
                delete_file(os.path.join(app.config['IMAGE_FOLDER'] , user.image))
            
            image_filename = 'a' + str(uuid.uuid4()) +'.' + image.filename.split('.')[-1]
            user.image = image_filename

            if image_filename:
                image.save(os.path.join(app.config['IMAGE_FOLDER'] , image_filename))

        if language not in empty:
            user.language = language

        db.session.add(user)
        db.session.commit()

        return {"message": "success"}
