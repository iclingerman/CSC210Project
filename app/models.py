from datetime import datetime
from app import db, login
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    name = db.Column(db.String(64))
    email = db.Column(db.String(120), index=True, unique=True)
    email_confirmed = db.Column(db.Boolean)
    confirmation_code = db.Column(db.Integer)

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


@login.user_loader
def load_user(id):
    return User.query.get(int(id))

class Calendars(db.Model):
    userid = db.Column(db.Integer, unique=True)
    calendarid = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))

class Events(db.Model):
    calendarid = db.Column(db.Integer)
    eventid = db.Column(db.Integer, primary_key=True)
    DOW = db.Column(db.Integer)
    start_time = db.Column(db.Time)
    end_time = db.Column(db.Time)
    name = db.Column(db.String(64))
    notification = db.Column(db.String(1))

class Share(db.Model):
    calendarid = db.Column(db.Integer, primary_key=True)
    friendid = db.Column(db.Integer, primary_key=True)

class Reset(db.Model):
    userid = db.Column(db.Integer, primary_key=True)
    reset_code = db.Column(db.Integer)
    timestamp = db.Column(db.Time)
    date = db.Column(db.Date)
