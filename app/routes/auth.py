from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required, current_user

from app.services.auth_service import authenticate, email_taken, register_user
from app.utils.validators import validate_signup

auth_bp = Blueprint("auth", __name__)


def _home_for(user):
    return url_for("admin.dashboard") if user.is_admin else url_for("user.dashboard")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(_home_for(current_user))

    if request.method == "POST":
        user = authenticate(request.form.get("email"), request.form.get("password"))
        if user is None:
            flash("That email and password don't match an account.", "error")
            return render_template("auth/login.html", email=request.form.get("email", ""))

        login_user(user, remember=bool(request.form.get("remember")))
        flash(f"Welcome back, {user.name}.", "success")
        nxt = request.args.get("next")
        return redirect(nxt if nxt and nxt.startswith("/") else _home_for(user))

    return render_template("auth/login.html", email="")


@auth_bp.route("/signup", methods=["GET", "POST"])
def signup():
    if current_user.is_authenticated:
        return redirect(_home_for(current_user))

    if request.method == "POST":
        form = request.form
        errors = validate_signup(form)
        if not errors and email_taken(form.get("email", "")):
            errors.append("An account already uses that email.")

        if errors:
            for e in errors:
                flash(e, "error")
            return render_template("auth/signup.html", form=form)

        user = register_user(form["name"], form["email"],
                             form.get("phone"), form["password"])
        login_user(user)
        flash("Account created. Pick a route to get started.", "success")
        return redirect(url_for("user.dashboard"))

    return render_template("auth/signup.html", form={})


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Signed out.", "info")
    return redirect(url_for("main.index"))
