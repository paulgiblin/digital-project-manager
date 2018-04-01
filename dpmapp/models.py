from . import db

# This simple DB allows us to store key/value pairs persistently so we don't have to constantly reenter data
class SparkInfo(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    key = db.Column(db.String(128), unique=True)
    value = db.Column(db.String(128))
