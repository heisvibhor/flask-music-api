import json
from flask import request, current_app as app, jsonify
from werkzeug.security import check_password_hash
from flask_restful import reqparse
from .models import User
from instances import db, cache, jwt
from datetime import datetime, timezone
from functools import wraps
from flask_jwt_extended import jwt_required, get_jwt_identity, create_access_token

@jwt.user_lookup_loader
def user_lookup_callback(_jwt_header, jwt_data):
    identity = jwt_data["sub"]
    return User.query.filter_by(id=identity).one_or_none()

login_parser = reqparse.RequestParser()
login_parser.add_argument('email', required=True)
login_parser.add_argument('password', required=True)
@app.route('/login', methods=['POST'])
def login_post():
    args = login_parser.parse_args()
    email = args.get('email')
    password = args.get('password')

    user = User.query.filter(User.email == email).first()

    empty = [None, '']
    if email in empty or password in empty:
        return jsonify({"message":"invalid credentials"}), 406

    if user != None:
        if check_password_hash( user.password, password):
            
            return jsonify({
                'token': create_access_token(identity=user.id, additional_claims={"user_type": user.user_type}),
                'user_id': user.id,
                'user_type': user.user_type,
                'email': user.email,
                'message':'success'
            })
        else:
            return jsonify({"message":"invalid password"}), 401
    else:
        return jsonify({"message":"invalid email"}), 406

@cache.memoize()
def getUser(user_id):
    return User.query.filter_by(id=user_id).first()

