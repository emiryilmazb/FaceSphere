from extensions import db


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    department = db.Column(db.String(50))
    phone_number = db.Column(db.String(20))
    entry_time = db.Column(db.String(20))
    exit_time = db.Column(db.String(20))
    photo_location = db.Column(db.String(100))


class AccessLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    attempt_time = db.Column(db.String(20))
