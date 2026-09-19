from datetime import datetime, date
from app import db


class Reservation(db.Model):
    __tablename__ = "reservations"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    bus_id = db.Column(db.Integer, db.ForeignKey("buses.id"), nullable=False)
    route_id = db.Column(db.Integer, db.ForeignKey("routes.id"), nullable=False)
    seats = db.Column(db.Integer, nullable=False, default=1)
    travel_date = db.Column(db.Date, nullable=False, default=date.today)
    total_fare = db.Column(db.Float, default=0)
    status = db.Column(db.String(15), default="CONFIRMED")  # CONFIRMED | CANCELLED
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    @property
    def pnr(self):
        return f"SF{self.id:05d}"

    def to_dict(self):
        return {
            "id": self.id, "pnr": self.pnr,
            "passenger": self.user.name if self.user else "",
            "email": self.user.email if self.user else "",
            "bus_no": self.bus.bus_no if self.bus else "",
            "bus_name": self.bus.name if self.bus else "",
            "source": self.route.source if self.route else "",
            "destination": self.route.destination if self.route else "",
            "departure_time": self.route.departure_time if self.route else "",
            "seats": self.seats,
            "travel_date": self.travel_date.strftime("%d %b %Y"),
            "total_fare": self.total_fare,
            "status": self.status,
        }

    def __repr__(self):
        return f"<Reservation {self.pnr}>"
