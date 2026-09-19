from datetime import date

from flask import (Blueprint, render_template, redirect, url_for,
                   request, flash, abort)
from flask_login import login_required, current_user

from app import db
from app.models import Bus, Route, Reservation, Feedback
from app.services.booking_service import (create_reservation, cancel_reservation,
                                          delete_reservation, seats_available)
from app.services.auth_service import update_profile
from app.utils.validators import parse_date, to_int, validate_booking

user_bp = Blueprint("user", __name__)


@user_bp.before_request
@login_required
def block_admins():
    """Admins have their own screens; keep the two areas separate."""
    if current_user.is_admin:
        return redirect(url_for("admin.dashboard"))


# ---------- dashboard ----------
@user_bp.route("/dashboard")
def dashboard():
    bookings = (Reservation.query
                .filter_by(user_id=current_user.id)
                .order_by(Reservation.travel_date.desc()).all())
    upcoming = [b for b in bookings
                if b.status == "CONFIRMED" and b.travel_date >= date.today()]
    return render_template("user/dashboard.html",
                           bookings=bookings[:5],
                           upcoming=upcoming,
                           total_trips=len(bookings),
                           routes=Route.query.limit(4).all())


# ---------- viewBus ----------
@user_bp.route("/buses")
def view_bus():
    return render_template("user/view_bus.html", buses=Bus.query.all())


# ---------- viewRoute ----------
@user_bp.route("/routes")
def view_route():
    source = request.args.get("source", "").strip()
    destination = request.args.get("destination", "").strip()

    query = Route.query
    if source:
        query = query.filter(Route.source.ilike(f"%{source}%"))
    if destination:
        query = query.filter(Route.destination.ilike(f"%{destination}%"))

    return render_template("user/view_route.html", routes=query.all(),
                           source=source, destination=destination,
                           today=date.today().isoformat())


# ---------- reservations: view / add / delete ----------
@user_bp.route("/reservations")
def reservations():
    items = (Reservation.query.filter_by(user_id=current_user.id)
             .order_by(Reservation.created_at.desc()).all())
    return render_template("user/reservations.html", reservations=items)


@user_bp.route("/reservations/add", methods=["POST"])
def add_reservation():
    route_id = to_int(request.form.get("route_id"))
    seats = to_int(request.form.get("seats"), 1)
    travel_date = parse_date(request.form.get("travel_date"))

    errors = validate_booking(seats, travel_date)
    if errors:
        for e in errors:
            flash(e, "error")
        return redirect(url_for("user.view_route"))

    reservation, error = create_reservation(current_user, route_id, seats, travel_date)
    if error:
        flash(error, "error")
        return redirect(url_for("user.view_route"))

    flash(f"Booked. Your PNR is {reservation.pnr}.", "success")
    return redirect(url_for("user.reservations"))


@user_bp.route("/reservations/<int:res_id>/cancel", methods=["POST"])
def cancel(res_id):
    reservation = db.session.get(Reservation, res_id) or abort(404)
    if reservation.user_id != current_user.id:
        abort(403)
    ok, message = cancel_reservation(reservation)
    flash(message, "success" if ok else "error")
    return redirect(url_for("user.reservations"))


@user_bp.route("/reservations/<int:res_id>/delete", methods=["POST"])
def delete_res(res_id):
    reservation = db.session.get(Reservation, res_id) or abort(404)
    if reservation.user_id != current_user.id:
        abort(403)
    delete_reservation(reservation)
    flash("Booking removed from your history.", "success")
    return redirect(url_for("user.reservations"))


# ---------- feedback: add / view / update / delete ----------
@user_bp.route("/feedback")
def feedback():
    mine = (Feedback.query.filter_by(user_id=current_user.id)
            .order_by(Feedback.created_at.desc()).all())
    return render_template("user/feedback.html", feedbacks=mine)


@user_bp.route("/feedback/add", methods=["POST"])
def add_feedback():
    message = request.form.get("message", "").strip()
    rating = to_int(request.form.get("rating"), 5)
    if not message:
        flash("Write a few words before posting.", "error")
        return redirect(url_for("user.feedback"))

    db.session.add(Feedback(user_id=current_user.id, message=message,
                            rating=min(max(rating, 1), 5)))
    db.session.commit()
    flash("Thanks — your feedback is posted.", "success")
    return redirect(url_for("user.feedback"))


@user_bp.route("/feedback/<int:fb_id>/update", methods=["POST"])
def update_feedback(fb_id):
    fb = db.session.get(Feedback, fb_id) or abort(404)
    if fb.user_id != current_user.id:
        abort(403)

    message = request.form.get("message", "").strip()
    if not message:
        flash("Feedback cannot be empty.", "error")
        return redirect(url_for("user.feedback"))

    fb.message = message
    fb.rating = min(max(to_int(request.form.get("rating"), fb.rating), 1), 5)
    db.session.commit()
    flash("Feedback updated.", "success")
    return redirect(url_for("user.feedback"))


@user_bp.route("/feedback/<int:fb_id>/delete", methods=["POST"])
def delete_feedback(fb_id):
    fb = db.session.get(Feedback, fb_id) or abort(404)
    if fb.user_id != current_user.id:
        abort(403)
    db.session.delete(fb)
    db.session.commit()
    flash("Feedback deleted.", "success")
    return redirect(url_for("user.feedback"))


# ---------- profile ----------
@user_bp.route("/profile", methods=["GET", "POST"])
def profile():
    if request.method == "POST":
        update_profile(current_user,
                       name=request.form.get("name"),
                       phone=request.form.get("phone"),
                       password=request.form.get("password") or None)
        flash("Profile saved.", "success")
        return redirect(url_for("user.profile"))
    return render_template("user/profile.html")
