from flask import current_app as app, send_file
import os
@app.route("/api/audio/<string:filename>")
def return_audio(filename):
    name = os.path.join(app.config['AUDIO_FOLDER'] , filename)
    if os.path.exists(name):
        return send_file(name)
    else:
        return None, 404

@app.route("/api/image/<string:filename>")
def return_image(filename):
    name = os.path.join(app.config['IMAGE_FOLDER'] , filename)
    if os.path.exists(name):
        return send_file(name)
    else:
        return send_file(app.config['IMAGE_FOLDER'] +"/default.jpg")