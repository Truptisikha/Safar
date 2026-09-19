from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    phone = db.Column(db.String(15))
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(10), nullable=False, default="user")  # user | admin
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    reservations = db.relationship("Reservation", backref="user",
                                   cascade="all, delete-orphan", lazy=True)
    feedbacks = db.relationship("Feedback", backref="user",
                                cascade="all, delete-orphan", lazy=True)

    def set_password(self, raw):
        self.password_hash = generate_password_hash(raw)

    def check_password(self, raw):
        return check_password_hash(self.password_hash, raw)

    @property
    def is_admin(self):
        return self.role == "admin"

    def to_dict(self):
        return {
            "id": self.id, "name": self.name, "email": self.email,
            "phone": self.phone, "role": self.role,
            "joined": self.created_at.strftime("%d %b %Y") if self.created_at else "",
            "trips": len(self.reservations),
        }

    def __repr__(self):
        return f"<User {self.email} ({self.role})>"
