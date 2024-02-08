import json
from flask import request, current_app as app, jsonify
from werkzeug.security import generate_password_hash , check_password_hash
from flask_restful import reqparse
from .models import User
from instances import db
import jwt
from datetime import datetime, timezone
from functools import wraps

login_parser = reqparse.RequestParser()
login_parser.add_argument('username', required=True)
login_parser.add_argument('password', required=True)

def getToken(user):
    print(app.config["SECRET_KEY"])
    help(jwt.encode)
    help(jwt.decode)
    return jwt.encode({"user_id": user.id, "iat": datetime.now(tz=timezone.utc)} , app.config["SECRET_KEY"], algorithm="HS256")

@app.route('/login', methods=['POST'])
def login_post():
    args = login_parser.parse_args()
    username = args.get('username')
    password = args.get('password')

    user = User.query.filter(User.username == username).first()

    empty = [None, '']
    if username in empty or password in empty:
        return jsonify("invalid credentials")

    if user != None:
        if check_password_hash( user.password, password):
            return jsonify({
                'token': getToken(user),
                'user_id': user.id,
                'user_type': user.user_type,
                'email': user.email
            })
        else:
            return jsonify("invalid password")
    else:
        return jsonify("invalid username")

def token_required(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            token = request.headers['Authorization']
        if not token:
            return jsonify({"message": "missing token"})
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms='HS256')
            current_user = User.query.filter_by(id=data['user_id']).first()
        except:
            return jsonify({"message": "invalid"}), 401
        return f(current_user, *args, **kwargs)
    return decorator
