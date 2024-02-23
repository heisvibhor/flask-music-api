from flask import Flask
from flask_sqlalchemy import SQLAlchemy 
from flask_caching import Cache
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_marshmallow import Marshmallow

cache = Cache()
app = Flask(__name__)
CORS(app)
jwt = JWTManager(app)
db = SQLAlchemy()
ma = Marshmallow(app)