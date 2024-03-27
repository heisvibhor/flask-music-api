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

forgot = reqparse.RequestParser()
forgot.add_argument('email', required=True, location=["form"])

@app.route('/api/forgot_password', methods=['POST'])
def fgtpassword():
    email = request.form.get("email") 
    user = User.query.where(User.email == email).first()

    if not user:
        return {"message": "email not found try signing up"}, 404
    
    regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
    if re.fullmatch(regex, email):
        msg = EmailMessage()
        msg.set_content(f"Use {getOTP(email)} to verify for Vibhorify")
        msg['Subject'] = 'Verify OTP for vibhorify'
        msg['To'] = email
        # send_mail(msg)
    else:
        return jsonify({"message": "invalid email address"}), 406

    return jsonify({"message": "OTP send"}), 200

    
@app.route('/api/change_password', methods=["POST"])
def changepswd():
    email = request.form.get("email") 
    password = request.form.get("password") 
    otp = request.form.get("OTP") 
    user = User.query.where(User.email == email).first()

    if not user:
        return {"message": "email not found try signing up"}, 404
    if password.strip() != password or len(password) < 6 :
        return {"message": "invalid password"}, 400
    
    OTP = getOTP(email)
    if otp != OTP:
        return {"message": "invalid otp"}, 400
    
    user.password = generate_password_hash(password)
    db.session.add(user)
    db.session.commit()
    return {"message": "change password success"}, 400
    

@cache.memoize(300)
def getOTP(email_id):
    return random.randint(100000, 999999)

# @app.errorhandler(BadRequest)
# def handle_bad_request(e):
#     return jsonify({"message": "bad request"}), 400

@app.route('/api/get_otp', methods=['POST'])
def get_mail_otp():
    email = request.form.get("email")
    user = User.query.where(User.email == email).first()
    if user:
        return jsonify({"message": "Email already exists try login"}), 406
    
    regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
    if re.fullmatch(regex, email):
        msg = EmailMessage()
        msg.set_content(f"Use {getOTP(email)} to verify for Vibhorify")
        msg['Subject'] = 'Vibhorify ' 
        msg['To'] = email
        send_mail(msg)
    else:
        return jsonify({"message": "Invalid email address"}), 406

    return jsonify({"message": "success"}), 200