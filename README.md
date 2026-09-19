# Safar.com — Bus Management System

A Flask bus reservation system with two roles, built to the SRS mind map:
passengers search routes and manage their own bookings and feedback; admins
manage the fleet, routes, bookings, passengers and reviews.

## Stack
Flask · Flask-SQLAlchemy · Flask-Login · Jinja2 · vanilla JS · SQLite (swap for
MySQL/PostgreSQL by changing `DATABASE_URL`).

## Run it

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env            # then edit SECRET_KEY
python seed.py                  # optional sample data
python app.py
```

Open http://127.0.0.1:5000

Seed logins: `admin@safar.com / admin123` and `riya@mail.com / user123`.

## Feature map (SRS → code)

| SRS node | Where it lives |
|---|---|
| Login / SignUp / logout | `app/routes/auth.py` |
| User → viewBus | `user.view_bus` |
| User → viewRoute | `user.view_route` |
| User → add/delete/viewReservation | `user.add_reservation`, `user.cancel`, `user.delete_res`, `user.reservations` |
| User → add/update/delete/viewFeedBack | `user.add_feedback`, `user.update_feedback`, `user.delete_feedback`, `user.feedback` |
| Admin → Bus add/update/delete/view | `admin.add_bus`, `admin.update_bus`, `admin.delete_bus`, `admin.manage_bus` |
| Admin → viewAllReservation / viewReservationById | `admin.reservations`, `admin.reservation_detail` |
| Admin → Route add/update/view/delete | `admin.add_route`, `admin.update_route`, `admin.manage_route`, `admin.delete_route` |
| Admin → viewFeedBack | `admin.feedback` |
| Admin → deleteUser / viewUser | `admin.delete_user`, `admin.users` |
| Admin → update | `admin.profile` |

## Database

`users` — id, name, email (unique), phone, password_hash, role, created_at
`buses` — id, bus_no (unique), name, bus_type, total_seats
`routes` — id, source, destination, distance_km, fare, departure_time, arrival_time, bus_id → buses
`reservations` — id, user_id, bus_id, route_id, seats, travel_date, total_fare, status
`feedbacks` — id, user_id, message, rating, created_at, updated_at

Deleting a bus cascades to its routes and reservations; deleting a user cascades
to their reservations and feedback.

## Notes

- Passwords are hashed with Werkzeug; nothing is stored in plain text.
- Seat availability is computed per route **per travel date**, so the same bus
  can be full on Friday and empty on Saturday (`app/services/booking_service.py`).
- `/api/*` returns JSON for the JavaScript — live seat counts and booking
  without a page reload.
