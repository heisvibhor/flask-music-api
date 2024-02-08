from instances import db, app
from main import *

with app.app_context():
    db.create_all()