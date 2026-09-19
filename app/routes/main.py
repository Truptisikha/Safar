from flask import Blueprint, render_template, redirect, url_for
from flask_login import current_user
from app.models import Route, Feedback

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def index():
    if current_user.is_authenticated:
        return redirect(url_for("admin.dashboard" if current_user.is_admin
                                else "user.dashboard"))
    routes = Route.query.limit(6).all()
    reviews = Feedback.query.order_by(Feedback.created_at.desc()).limit(3).all()
    return render_template("index.html", routes=routes, reviews=reviews)
