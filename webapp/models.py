from datetime import datetime
from . import db
from werkzeug.security import generate_password_hash, check_password_hash


# user table
class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)

    # user email (must be unique)
    email = db.Column(db.String(255), unique=True, nullable=False)

    # hashed password (never store raw password)
    password_hash = db.Column(db.String(255), nullable=False)

    # set password when registering
    def set_password(self, password: str):
        self.password_hash = generate_password_hash(password)

    # check password on login
    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)


# stores each simulation session
class Simulation(db.Model):
    __tablename__ = "simulations"

    id = db.Column(db.Integer, primary_key=True)

    # which user started it (optional)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)

    # current state of simulation (fsm state)
    state = db.Column(db.String(50), nullable=False, default="INITIAL_PHISH")

    # difficulty level
    difficulty = db.Column(db.String(20), nullable=False, default="easy")

    # type of attack (phishing, delivery, etc)
    attack_type = db.Column(db.String(30), nullable=False, default="phishing")

    # tracks how risky user actions are
    risk_score = db.Column(db.Integer, nullable=False, default=0)

    # when simulation was created
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)


# logs every event in simulation
class SimulationEvent(db.Model):
    __tablename__ = "simulation_events"

    id = db.Column(db.Integer, primary_key=True)

    # link to simulation
    simulation_id = db.Column(db.Integer, db.ForeignKey("simulations.id"), nullable=False)

    # type of event (attack message, user action, etc)
    event_type = db.Column(db.String(50), nullable=False)

    # actual message or action content
    content = db.Column(db.Text, nullable=False)

    # timestamp of event
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)