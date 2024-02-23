import uuid, os, random, re
from flask import request, jsonify
from instances import app, db, cache
from .models import User
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.exceptions import BadRequest
from werkzeug.datastructures import FileStorage
from flask_restful import reqparse
from email.message import EmailMessage
from .mail import send_mail
from flask_jwt_extended import create_access_token

signup_parser = reqparse.RequestParser()
signup_parser.add_argument('username', type=str, required=True, location=["form"])
signup_parser.add_argument('password', required=True, location=["form"])
signup_parser.add_argument('email', required=True, location=["form"])
signup_parser.add_argument('name', required=True, location=["form"])
signup_parser.add_argument('language', required=True, location=["form"])
signup_parser.add_argument('image', type=FileStorage, location=['files'])

@app.route('/signup', methods=['POST'])
def signup_post():
    args = signup_parser.parse_args()
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

@cache.memoize()
def getOTP(email_id):
    return random.randint(100000, 999999)

# @app.errorhandler(BadRequest)
# def handle_bad_request(e):
#     return jsonify({"message": "bad request"}), 400

@app.route('/get_otp', methods=['POST'])
def get_mail_otp():
    email = request.form.get("email")
    user = User.query.where(User.email == email).first()
    if user:
        return jsonify({"message": "email already exists"}), 406
    
    regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
    if re.fullmatch(regex, email):
        msg = EmailMessage()
        msg.set_content("message")
        msg['Subject'] = 'Verify OTP for vibhorify'
        msg['To'] = email
        # send_mail(msg)
    else:
        return jsonify({"message": "invalid email address"}), 406

    return jsonify({"message": "success"}), 200