import json
from flask import request, current_app as app, jsonify
from werkzeug.security import check_password_hash
from flask_restful import reqparse
from .models import User
from instances import db, cache
import jwt
from datetime import datetime, timezone
from functools import wraps

@cache.memoize()
def getToken(user_id):
    print('Saved by cache')
    return jwt.encode({"user_id": user_id, "iat": datetime.now(tz=timezone.utc)} , app.config["SECRET_KEY"], algorithm="HS256")

login_parser = reqparse.RequestParser()
login_parser.add_argument('username', required=True)
login_parser.add_argument('password', required=True)
@app.route('/login', methods=['POST'])
def login_post():
    args = login_parser.parse_args()
    username = args.get('username')
    password = args.get('password')

    user = User.query.filter(User.username == username).first()

    empty = [None, '']
    if username in empty or password in empty:
        return jsonify({"message":"invalid credentials"}), 406

    if user != None:
        if check_password_hash( user.password, password):
            return jsonify({
                'token': getToken(user.id),
                'user_id': user.id,
                'user_type': user.user_type,
                'email': user.email,
                'message':'success'
            })
        else:
            return jsonify({"message":"invalid password"}), 401
    else:
        return jsonify({"message":"invalid username"}), 406

def getUser(user_id):
    return User.query.filter_by(id=user_id).first()

def parseToken(token):
    user = None
    expired = True
    invalid = True
    try:
        data = jwt.decode(token, app.config['SECRET_KEY'], algorithms='HS256')
        user = getUser(data['user_id'])
        expired = False if datetime.now(tz=timezone.utc) - datetime.timedelta(days=4) < data['iat'] else True
    except:
        return user, expired, invalid
    if user == None:
        return user, expired, invalid
    return user, expired, False

def token_required(f):
    @wraps(f)
    def decorator(*args, **kwargs): 
        token = None
        if 'Authorization' in request.headers:
            token = request.headers['Authorization']
        if not token:
            return jsonify({"message": "missing token"}), 406
        user, expired, invalid = parseToken(token)
        if invalid: 
            return jsonify({"message": "invalid"}), 400
        if expired:
            return jsonify({"message": "token expired"}), 401
        return f(user, *args, **kwargs)
    return decorator

def admin_required(f):
    @wraps(f)
    def decorator(*args, **kwargs): 
        token = None
        if 'Authorization' in request.headers:
            token = request.headers['Authorization']
        if not token:
            return jsonify({"message": "missing token"}),406
        
        user, expired, invalid = parseToken(token)
        if invalid: 
            return jsonify({"message": "invalid"}), 400
        if expired:
            return jsonify({"message": "token expired"}), 401
        if user.user_type != 'ADMIN':
            return  jsonify({"message": "invalid access"}), 403
        return f(user, *args, **kwargs)
    return decorator


def creator_required(f):
    @wraps(f)
    def decorator(*args, **kwargs): 
        token = None
        if 'Authorization' in request.headers:
            token = request.headers['Authorization']
        if not token:
            return jsonify({"message": "missing token"}), 406
        user, expired, invalid = parseToken(token)
        if invalid: 
            return jsonify({"message": "invalid"}), 400
        if expired:
            return jsonify({"message": "token expired"}), 401
        if user.user_type != 'CREATOR':
            return  jsonify({"message": "invalid access"}), 403
        return f(user, *args, **kwargs)
    return decorator