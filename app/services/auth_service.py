"""Account creation and sign-in logic."""
from app import db
from app.models import User


def email_taken(email):
    return User.query.filter_by(email=email.strip().lower()).first() is not None


def register_user(name, email, phone, password, role="user"):
    user = User(
        name=name.strip(),
        email=email.strip().lower(),
        phone=(phone or "").strip(),
        role=role,
    )
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    return user


def authenticate(email, password):
    """Returns the User on success, otherwise None."""
    user = User.query.filter_by(email=(email or "").strip().lower()).first()
    if user and user.check_password(password or ""):
        return user
    return None


def update_profile(user, name=None, phone=None, password=None):
    if name:
        user.name = name.strip()
    if phone is not None:
        user.phone = phone.strip()
    if password:
        user.set_password(password)
    db.session.commit()
    return user
