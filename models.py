from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from app import db

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(20), unique=True)
    email = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(128))  # Увеличил длину поля для пароля
    
    images = db.relationship('Image', back_populates='user', lazy=True)

    def __repr__(self):
        return '<User %r>' % self.id

    def set_password(self, password):
        self.password = generate_password_hash(password)
        return self.password
        
    def check_password(self, password):
        return check_password_hash(self.password, password)

class Image(db.Model):
    __tablename__ = 'images'
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    path = db.Column(db.String(255), nullable=False)
    image_metadata = db.Column(db.String(255))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    user = db.relationship('User', back_populates='images')

    def __repr__(self):
        return '<Image %r>' % self.id