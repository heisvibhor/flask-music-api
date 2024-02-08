from instances import db, app
import os
from dotenv import load_dotenv

load_dotenv()


with app.app_context():
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('SQLALCHEMY_DATABASE_URI')
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
    app.config['IMAGE_FOLDER'] = os.environ.get('IMAGE_FOLDER')
    app.config['AUDIO_FOLDER'] = os.environ.get('AUDIO_FOLDER')
    db.init_app(app)
app.app_context().push()

from application.login import *
from application.api import *


if __name__ == '__main__':
    app.run(host='::', port ="5001", debug=True, threaded = False)