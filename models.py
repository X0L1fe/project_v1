from flask_sqlalchemy import SQLAlchemy
from flask import Flask

from app import db

app = Flask(__name__)
app.config['SECRET_KEY'] ='secret-pzdc'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///profile.db'

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(20), unique=True)
    email = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(20))
    image = db.Column(db.LargeBinary)

    def __repr__(self):
        return '<User %r>' % self.id

db = SQLAlchemy(app)

if __name__ == "__main__":
    app.run(debug=True)