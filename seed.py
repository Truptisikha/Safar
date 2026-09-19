"""Fill a fresh database with an admin, sample passengers, buses and routes.

    python seed.py
"""
from datetime import date, timedelta

from app import create_app, db
from app.models import User, Bus, Route, Reservation, Feedback

app = create_app()

BUSES = [
    ("OD02AB1234", "Konark Express", "AC Seater", 40),
    ("OD05CD5678", "Chilika Rider",  "Sleeper",   30),
    ("OD07EF9012", "Utkal Deluxe",   "AC Sleeper", 36),
    ("WB12GH3456", "Coastal Line",   "Seater",    45),
]

ROUTES = [
    ("Bhubaneswar", "Kolkata",     480, 850, "21:00", "06:30", 0),
    ("Bhubaneswar", "Puri",         60, 150, "07:00", "08:30", 1),
    ("Cuttack",     "Visakhapatnam", 440, 790, "20:30", "06:00", 2),
    ("Bhubaneswar", "Sambalpur",    300, 520, "06:00", "12:00", 3),
    ("Puri",        "Bhubaneswar",   60, 150, "18:00", "19:30", 1),
]


def run():
    with app.app_context():
        db.drop_all()
        db.create_all()

        admin = User(name="Depot Admin", email="admin@safar.com",
                     phone="9876543210", role="admin")
        admin.set_password("admin123")

        riya = User(name="Riya Mohanty", email="riya@mail.com", phone="9000000001")
        riya.set_password("user123")

        arjun = User(name="Arjun Das", email="arjun@mail.com", phone="9000000002")
        arjun.set_password("user123")

        db.session.add_all([admin, riya, arjun])
        db.session.commit()

        buses = [Bus(bus_no=n, name=nm, bus_type=t, total_seats=s)
                 for n, nm, t, s in BUSES]
        db.session.add_all(buses)
        db.session.commit()

        routes = []
        for src, dst, km, fare, dep, arr, bus_index in ROUTES:
            routes.append(Route(source=src, destination=dst, distance_km=km,
                                fare=fare, departure_time=dep, arrival_time=arr,
                                bus_id=buses[bus_index].id))
        db.session.add_all(routes)
        db.session.commit()

        soon = date.today() + timedelta(days=3)
        later = date.today() + timedelta(days=10)
        db.session.add_all([
            Reservation(user_id=riya.id, bus_id=routes[0].bus_id, route_id=routes[0].id,
                        seats=2, travel_date=soon, total_fare=routes[0].fare * 2),
            Reservation(user_id=arjun.id, bus_id=routes[1].bus_id, route_id=routes[1].id,
                        seats=1, travel_date=later, total_fare=routes[1].fare),
        ])

        db.session.add_all([
            Feedback(user_id=riya.id, rating=5,
                     message="Left on time and the overnight seat actually reclined. "
                             "Booking took under a minute."),
            Feedback(user_id=arjun.id, rating=4,
                     message="Clean bus and a polite driver. One extra stop on the way "
                             "that wasn't on the schedule."),
        ])
        db.session.commit()

        print("Seeded.")
        print("  admin@safar.com / admin123")
        print("  riya@mail.com   / user123")


if __name__ == "__main__":
    run()
