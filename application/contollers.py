from flask import current_app as app, send_file
from functools import wraps
from flask_jwt_extended import jwt_required, get_jwt, get_jwt_identity
import os
from datetime import datetime
from instances import redisInstance

@app.route("/api/audio/<string:filename>")
def return_audio(filename):
    name = os.path.join(app.config['AUDIO_FOLDER'] , filename)
    if os.path.exists(name):
        return send_file(name)
    else:
        return {"message": "not found"}, 404

@app.route("/api/image/<string:filename>")
def return_image(filename):
    name = os.path.join(app.config['IMAGE_FOLDER'] , filename)
    if os.path.exists(name):
        return send_file(name)
    else:
        return send_file(app.config['IMAGE_FOLDER'] +"/default.jpg")
    
def user(f):
    @wraps(f)
    def _user(*args, **kwargs):
        redisInstance.set('last_login_' + str(get_jwt_identity()), str(datetime.now()))
        return f(*args, **kwargs)
    return _user