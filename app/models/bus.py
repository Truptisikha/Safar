from datetime import datetime
from app import db


class Bus(db.Model):
    __tablename__ = "buses"

    id = db.Column(db.Integer, primary_key=True)
    bus_no = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(80), nullable=False)
    bus_type = db.Column(db.String(30), default="Seater")   # Seater | Sleeper | AC Seater | AC Sleeper
    total_seats = db.Column(db.Integer, nullable=False, default=40)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    routes = db.relationship("Route", backref="bus",
                             cascade="all, delete-orphan", lazy=True)
    reservations = db.relationship("Reservation", backref="bus",
                                   cascade="all, delete-orphan", lazy=True)

    def to_dict(self):
        return {
            "id": self.id, "bus_no": self.bus_no, "name": self.name,
            "bus_type": self.bus_type, "total_seats": self.total_seats,
            "routes": len(self.routes),
        }

    def __repr__(self):
        return f"<Bus {self.bus_no}>"
