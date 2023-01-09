import hashlib

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Signs(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.String(128), unique=True)
    sign_id = db.Column(db.String(128), unique=True)
    config = db.Column(db.JSON)
    claim_code = db.Column(db.String(128), nullable=True, unique=True)
