from flask import Flask
from flask_sqlalchemy import SQLAlchemy 
from flask_caching import Cache

cache = Cache()
app = Flask(__name__)
db = SQLAlchemy()