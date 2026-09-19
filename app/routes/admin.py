from flask import (Blueprint, render_template, redirect, url_for,
                   request, flash, abort)
from flask_login import current_user

from app import db
from app.models import User, Bus, Route, Reservation, Feedback
from app.utils.decorators import admin_required
from app.utils.validators import to_int, to_float
from app.services.auth_service import update_profile

admin_bp = Blueprint("admin", __name__)


@admin_bp.before_request
@admin_required
def guard():
    """Every admin view is admin-only."""
    return None


# ---------- dashboard ----------
@admin_bp.route("/dashboard")
def dashboard():
    recent = (Reservation.query.order_by(Reservation.created_at.desc())
              .limit(8).all())
    stats = {
        "buses": Bus.query.count(),
        "routes": Route.query.count(),
        "bookings": Reservation.query.filter_by(status="CONFIRMED").count(),
        "passengers": User.query.filter_by(role="user").count(),
        "revenue": round(sum(r.total_fare for r in
                             Reservation.query.filter_by(status="CONFIRMED").all()), 2),
    }
    return render_template("admin/dashboard.html", stats=stats, recent=recent)


# ---------- bus: add / update / delete / view ----------
@admin_bp.route("/buses")
def manage_bus():
    return render_template("admin/manage_bus.html", buses=Bus.query.all())


@admin_bp.route("/buses/add", methods=["POST"])
def add_bus():
    bus_no = request.form.get("bus_no", "").strip().upper()
    if not bus_no or not request.form.get("name", "").strip():
        flash("Bus number and name are required.", "error")
        return redirect(url_for("admin.manage_bus"))
    if Bus.query.filter_by(bus_no=bus_no).first():
        flash(f"Bus {bus_no} already exists.", "error")
        return redirect(url_for("admin.manage_bus"))

    db.session.add(Bus(
        bus_no=bus_no,
        name=request.form["name"].strip(),
        bus_type=request.form.get("bus_type", "Seater"),
        total_seats=to_int(request.form.get("total_seats"), 40),
    ))
    db.session.commit()
    flash(f"Bus {bus_no} added.", "success")
    return redirect(url_for("admin.manage_bus"))


@admin_bp.route("/buses/<int:bus_id>/update", methods=["POST"])
def update_bus(bus_id):
    bus = db.session.get(Bus, bus_id) or abort(404)
    bus.bus_no = request.form.get("bus_no", bus.bus_no).strip().upper()
    bus.name = request.form.get("name", bus.name).strip()
    bus.bus_type = request.form.get("bus_type", bus.bus_type)
    bus.total_seats = to_int(request.form.get("total_seats"), bus.total_seats)
    db.session.commit()
    flash(f"Bus {bus.bus_no} updated.", "success")
    return redirect(url_for("admin.manage_bus"))


@admin_bp.route("/buses/<int:bus_id>/delete", methods=["POST"])
def delete_bus(bus_id):
    bus = db.session.get(Bus, bus_id) or abort(404)
    db.session.delete(bus)     # routes + reservations cascade
    db.session.commit()
    flash(f"Bus {bus.bus_no} deleted, along with its routes and bookings.", "success")
    return redirect(url_for("admin.manage_bus"))


# ---------- route: add / update / view / delete ----------
@admin_bp.route("/routes")
def manage_route():
    return render_template("admin/manage_route.html",
                           routes=Route.query.all(), buses=Bus.query.all())


@admin_bp.route("/routes/add", methods=["POST"])
def add_route():
    bus_id = to_int(request.form.get("bus_id"))
    if not db.session.get(Bus, bus_id):
        flash("Pick a bus for this route.", "error")
        return redirect(url_for("admin.manage_route"))

    db.session.add(Route(
        source=request.form.get("source", "").strip(),
        destination=request.form.get("destination", "").strip(),
        distance_km=to_float(request.form.get("distance_km")),
        fare=to_float(request.form.get("fare")),
        departure_time=request.form.get("departure_time", "06:00"),
        arrival_time=request.form.get("arrival_time", "12:00"),
        bus_id=bus_id,
    ))
    db.session.commit()
    flash("Route added.", "success")
    return redirect(url_for("admin.manage_route"))


@admin_bp.route("/routes/<int:route_id>/update", methods=["POST"])
def update_route(route_id):
    route = db.session.get(Route, route_id) or abort(404)
    route.source = request.form.get("source", route.source).strip()
    route.destination = request.form.get("destination", route.destination).strip()
    route.distance_km = to_float(request.form.get("distance_km"), route.distance_km)
    route.fare = to_float(request.form.get("fare"), route.fare)
    route.departure_time = request.form.get("departure_time", route.departure_time)
    route.arrival_time = request.form.get("arrival_time", route.arrival_time)
    route.bus_id = to_int(request.form.get("bus_id"), route.bus_id)
    db.session.commit()
    flash("Route updated.", "success")
    return redirect(url_for("admin.manage_route"))


@admin_bp.route("/routes/<int:route_id>/delete", methods=["POST"])
def delete_route(route_id):
    route = db.session.get(Route, route_id) or abort(404)
    db.session.delete(route)
    db.session.commit()
    flash("Route deleted.", "success")
    return redirect(url_for("admin.manage_route"))


# ---------- reservations: all / by id ----------
@admin_bp.route("/reservations")
def reservations():
    status = request.args.get("status", "")
    query = Reservation.query
    if status in ("CONFIRMED", "CANCELLED"):
        query = query.filter_by(status=status)
    items = query.order_by(Reservation.created_at.desc()).all()
    return render_template("admin/reservations.html",
                           reservations=items, status=status)


@admin_bp.route("/reservations/<int:res_id>")
def reservation_detail(res_id):
    reservation = db.session.get(Reservation, res_id) or abort(404)
    return render_template("admin/reservation_detail.html", r=reservation)


# ---------- feedback: view ----------
@admin_bp.route("/feedback")
def feedback():
    items = Feedback.query.order_by(Feedback.created_at.desc()).all()
    average = round(sum(f.rating for f in items) / len(items), 1) if items else 0
    return render_template("admin/feedback.html", feedbacks=items, average=average)


@admin_bp.route("/feedback/<int:fb_id>/delete", methods=["POST"])
def delete_feedback(fb_id):
    fb = db.session.get(Feedback, fb_id) or abort(404)
    db.session.delete(fb)
    db.session.commit()
    flash("Feedback removed.", "success")
    return redirect(url_for("admin.feedback"))


# ---------- user: view / delete ----------
@admin_bp.route("/users")
def users():
    return render_template("admin/users.html",
                           users=User.query.filter_by(role="user").all())


@admin_bp.route("/users/<int:user_id>/delete", methods=["POST"])
def delete_user(user_id):
    user = db.session.get(User, user_id) or abort(404)
    if user.is_admin:
        flash("Admin accounts can't be deleted here.", "error")
        return redirect(url_for("admin.users"))
    db.session.delete(user)
    db.session.commit()
    flash(f"{user.name}'s account was deleted.", "success")
    return redirect(url_for("admin.users"))


# ---------- update (admin's own profile) ----------
@admin_bp.route("/profile", methods=["GET", "POST"])
def profile():
    if request.method == "POST":
        update_profile(current_user,
                       name=request.form.get("name"),
                       phone=request.form.get("phone"),
                       password=request.form.get("password") or None)
        flash("Profile saved.", "success")
        return redirect(url_for("admin.profile"))
    return render_template("admin/profile.html")
