"""Entry point: flask run  (or)  python app.py"""
import os
from app import create_app, db

app = create_app(os.environ.get("FLASK_ENV", "development"))


@app.shell_context_processor
def shell_context():
    from app.models import User, Bus, Route, Reservation, Feedback
    return dict(db=db, User=User, Bus=Bus, Route=Route,
                Reservation=Reservation, Feedback=Feedback)


if __name__ == "__main__":
    app.run(debug=True)
