from app import db


class Route(db.Model):
    __tablename__ = "routes"

    id = db.Column(db.Integer, primary_key=True)
    source = db.Column(db.String(60), nullable=False)
    destination = db.Column(db.String(60), nullable=False)
    distance_km = db.Column(db.Float, default=0)
    fare = db.Column(db.Float, nullable=False, default=0)
    departure_time = db.Column(db.String(10), default="06:00")
    arrival_time = db.Column(db.String(10), default="12:00")
    bus_id = db.Column(db.Integer, db.ForeignKey("buses.id"), nullable=False)

    reservations = db.relationship("Reservation", backref="route",
                                   cascade="all, delete-orphan", lazy=True)

    def to_dict(self):
        return {
            "id": self.id, "source": self.source, "destination": self.destination,
            "distance_km": self.distance_km, "fare": self.fare,
            "departure_time": self.departure_time, "arrival_time": self.arrival_time,
            "bus_id": self.bus_id,
            "bus_no": self.bus.bus_no if self.bus else "",
            "bus_name": self.bus.name if self.bus else "",
        }

    def __repr__(self):
        return f"<Route {self.source}->{self.destination}>"
