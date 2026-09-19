from datetime import datetime
from app import db


class Feedback(db.Model):
    __tablename__ = "feedbacks"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    message = db.Column(db.Text, nullable=False)
    rating = db.Column(db.Integer, default=5)  # 1..5
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "author": self.user.name if self.user else "",
            "message": self.message,
            "rating": self.rating,
            "created": self.created_at.strftime("%d %b %Y"),
        }

    def __repr__(self):
        return f"<Feedback {self.id} by {self.user_id}>"
