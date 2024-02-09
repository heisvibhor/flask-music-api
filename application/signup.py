import uuid
import os
from flask import request, jsonify
from .login import getToken
from instances import app, db
from .models import User
from werkzeug.security import generate_password_hash, check_password_hash
from flask_restful import reqparse

signup_parser = reqparse.RequestParser()
signup_parser.add_argument('username', required=True)
signup_parser.add_argument('password', required=True)
signup_parser.add_argument('email', required=True)
signup_parser.add_argument('name', required=True)
signup_parser.add_argument('language', required=True)


@app.route('/signup', methods=['POST'])
def signup_post():
    args = signup_parser.parse_args()
    username = args.get('username')
    password = args.get('password')
    email = args.get('email')
    name = args.get('name')
    language = args.get('language')
    image = request.files['image']
    if image.filename == '':
        image_filename = None
    else:
        image_filename = 'a' + str(uuid.uuid4()) + \
            '.' + image.filename.split('.')[-1]
    if image_filename:
        image.save(os.path.join(app.config['IMAGE_FOLDER'], image_filename))

    empty = [None, '']

    if email in empty or username in empty or password in empty or name in empty or language in empty:
        return jsonify({"message": "invalid input"}), 406

    user = User.query.where(User.username == username).first()

    if user:
        return jsonify({"message": "username already exists"}), 406
    else:
        user = User(username=username, password=generate_password_hash(
            password), email=email, name=name, language=language, image=image_filename)
        db.session.add(user)
        db.session.commit()
        return jsonify({
            'token': getToken(user.id),
            'user_id': user.id,
            'user_type': user.user_type,
            'email': user.email,
            'message': 'success'
        }), 200


@app.route('/get_otp', methods=['POST'])
def get_mail_otp():
    email = request.args.get('email')
