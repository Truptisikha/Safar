"""JSON endpoints used by the front-end JavaScript."""
from flask import Blueprint, jsonify, request
from flask_login import current_user

from app import db
from app.models import Bus, Route, Reservation, Feedback
from app.services.booking_service import seats_available, create_reservation
from app.utils.decorators import api_login_required, api_admin_required
from app.utils.validators import parse_date, to_int, validate_booking

api_bp = Blueprint("api", __name__)


@api_bp.route("/buses")
@api_login_required
def buses():
    return jsonify({"ok": True, "data": [b.to_dict() for b in Bus.query.all()]})


@api_bp.route("/routes")
def routes():
    source = request.args.get("source", "").strip()
    destination = request.args.get("destination", "").strip()
    query = Route.query
    if source:
        query = query.filter(Route.source.ilike(f"%{source}%"))
    if destination:
        query = query.filter(Route.destination.ilike(f"%{destination}%"))
    return jsonify({"ok": True, "data": [r.to_dict() for r in query.all()]})


@api_bp.route("/routes/<int:route_id>/availability")
def availability(route_id):
    travel_date = parse_date(request.args.get("date", ""))
    if travel_date is None:
        return jsonify({"ok": False, "error": "Pick a travel date."}), 400
    free = seats_available(route_id, travel_date)
    route = db.session.get(Route, route_id)
    return jsonify({
        "ok": True,
        "seats_available": free,
        "fare": route.fare if route else 0,
    })


@api_bp.route("/reservations", methods=["POST"])
@api_login_required
def book():
    payload = request.get_json(silent=True) or {}
    seats = to_int(payload.get("seats"), 1)
    travel_date = parse_date(payload.get("travel_date", ""))

    errors = validate_booking(seats, travel_date)
    if errors:
        return jsonify({"ok": False, "error": errors[0]}), 400

    reservation, error = create_reservation(
        current_user, to_int(payload.get("route_id")), seats, travel_date)
    if error:
        return jsonify({"ok": False, "error": error}), 400

    return jsonify({"ok": True, "data": reservation.to_dict()}), 201


@api_bp.route("/reservations/mine")
@api_login_required
def my_reservations():
    items = (Reservation.query.filter_by(user_id=current_user.id)
             .order_by(Reservation.created_at.desc()).all())
    return jsonify({"ok": True, "data": [r.to_dict() for r in items]})


@api_bp.route("/admin/reservations")
@api_admin_required
def all_reservations():
    items = Reservation.query.order_by(Reservation.created_at.desc()).all()
    return jsonify({"ok": True, "data": [r.to_dict() for r in items]})


@api_bp.route("/feedback")
def feedback():
    items = Feedback.query.order_by(Feedback.created_at.desc()).limit(20).all()
    return jsonify({"ok": True, "data": [f.to_dict() for f in items]})
