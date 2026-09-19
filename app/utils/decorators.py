"""Role guards used across the admin blueprint."""
from functools import wraps
from flask import abort, redirect, url_for, flash, request, jsonify
from flask_login import current_user


def admin_required(view):
    @wraps(view)
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated:
            flash("Sign in as an admin to open that page.", "info")
            return redirect(url_for("auth.login", next=request.path))
        if not current_user.is_admin:
            abort(403)
        return view(*args, **kwargs)
    return wrapper


def api_login_required(view):
    """Same as login_required, but answers JSON instead of a redirect."""
    @wraps(view)
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated:
            return jsonify({"ok": False, "error": "Sign in to continue."}), 401
        return view(*args, **kwargs)
    return wrapper


def api_admin_required(view):
    @wraps(view)
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated:
            return jsonify({"ok": False, "error": "Sign in to continue."}), 401
        if not current_user.is_admin:
            return jsonify({"ok": False, "error": "Admins only."}), 403
        return view(*args, **kwargs)
    return wrapper
