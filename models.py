from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    is_verified = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, raw_password: str):
        self.password_hash = generate_password_hash(raw_password)

    def check_password(self, raw_password: str) -> bool:
        return check_password_hash(self.password_hash, raw_password)


class OTP(db.Model):
    __tablename__ = "otps"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), nullable=False, index=True)
    code = db.Column(db.String(6), nullable=False)
    purpose = db.Column(db.String(32), nullable=False, default="register")
    expires_at = db.Column(db.DateTime, nullable=False)
    consumed = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Song(db.Model):
    __tablename__ = "songs"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    kannada_text = db.Column(db.Text, nullable=False, default="")
    english_text = db.Column(db.Text, nullable=False, default="")
    original_filename = db.Column(db.String(255), nullable=True)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)

class ListedSong(db.Model):
    __tablename__ = "listed_songs"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    song_id = db.Column(
        db.Integer,
        db.ForeignKey("songs.id"),
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    user = db.relationship(
        "User",
        backref=db.backref("listed_songs", lazy=True)
    )

    song = db.relationship(
        "Song",
        backref=db.backref("listed_by_users", lazy=True)
    )
class Visitor(db.Model):
    __tablename__ = "visitors"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    email = db.Column(
        db.String(255),
        nullable=True
    )

    ip_address = db.Column(
        db.String(100),
        nullable=True
    )

    user_agent = db.Column(
        db.Text,
        nullable=True
    )

    page = db.Column(
        db.String(255),
        nullable=True
    )

    visited_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )