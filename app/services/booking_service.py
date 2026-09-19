"""Seat availability, fare calculation and cancellation rules."""
from datetime import date
from sqlalchemy import func
from app import db
from app.models import Reservation, Route, Bus


def seats_booked(bus_id, route_id, travel_date):
    total = (
        db.session.query(func.coalesce(func.sum(Reservation.seats), 0))
        .filter(
            Reservation.bus_id == bus_id,
            Reservation.route_id == route_id,
            Reservation.travel_date == travel_date,
            Reservation.status == "CONFIRMED",
        )
        .scalar()
    )
    return int(total or 0)


def seats_available(route_id, travel_date):
    route = db.session.get(Route, route_id)
    if not route:
        return 0
    bus = db.session.get(Bus, route.bus_id)
    if not bus:
        return 0
    return max(bus.total_seats - seats_booked(bus.id, route.id, travel_date), 0)


def calculate_fare(route, seats):
    return round(route.fare * seats, 2)


def create_reservation(user, route_id, seats, travel_date):
    """Returns (reservation, error_message)."""
    route = db.session.get(Route, route_id)
    if not route:
        return None, "That route no longer exists."

    free = seats_available(route.id, travel_date)
    if seats > free:
        return None, f"Only {free} seat(s) left on this trip."

    reservation = Reservation(
        user_id=user.id,
        bus_id=route.bus_id,
        route_id=route.id,
        seats=seats,
        travel_date=travel_date,
        total_fare=calculate_fare(route, seats),
        status="CONFIRMED",
    )
    db.session.add(reservation)
    db.session.commit()
    return reservation, None


def cancel_reservation(reservation):
    """Returns (ok, message)."""
    if reservation.status == "CANCELLED":
        return False, "This booking is already cancelled."
    if reservation.travel_date < date.today():
        return False, "A past trip cannot be cancelled."
    reservation.status = "CANCELLED"
    db.session.commit()
    return True, "Booking cancelled. Seats are back in the pool."


def delete_reservation(reservation):
    db.session.delete(reservation)
    db.session.commit()
