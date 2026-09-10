from flask import Blueprint, render_template
from . import db
from sqlalchemy import text
from .models import User, Simulation, SimulationEvent
from .simulation_engine import SimulationEngine
from flask import request
from .models import User

# main blueprint for all routes
main = Blueprint("main", __name__)


# home page
@main.route("/")
def home():
    return render_template("home.html")


# simulation page
@main.route("/test")
def test_page():
    return render_template("test.html")


# results page
@main.route("/results")
def results_page():
    return render_template("results.html")


# quick database test route
@main.route("/db-test")
def db_test():
    result = db.session.execute(text("SELECT 1")).scalar()
    return {"db_ok": True, "result": result}


# create a new simulation
@main.route("/start_simulation", methods=["POST"])
def start_simulation():
    from flask import request

    # get settings from frontend
    data = request.get_json(silent=True) or {}
    difficulty = data.get("difficulty", "easy")
    attack_type = data.get("attack_type", "phishing")
    user_id = data.get("user_id")

    # create simulation record
    sim = Simulation(
        user_id=user_id,
        state="INITIAL_PHISH",
        difficulty=difficulty,
        attack_type=attack_type
    )
    db.session.add(sim)
    db.session.commit()

    # choose first message based on attack type
    if attack_type == "delivery":
        first_msg = "Delivery Notice: Your parcel could not be delivered. Please confirm your address using the link provided."
    else:
        first_msg = "Hi, IT Support here — we detected unusual activity."

    # log first attacker message
    event = SimulationEvent(
        simulation_id=sim.id,
        event_type="ATTACK_MESSAGE",
        content=first_msg
    )
    db.session.add(event)
    db.session.commit()

    return {
        "simulation_id": sim.id,
        "state": sim.state,
        "difficulty": sim.difficulty,
        "attack_type": sim.attack_type,
        "message": first_msg
    }


# handle user response during simulation
@main.route("/respond", methods=["POST"])
def respond():
    from flask import request

    data = request.get_json()

    # find current simulation
    sim = Simulation.query.get(data.get("simulation_id"))

    if not sim:
        return {"error": "Simulation not found"}, 404

    user_action = data.get("action")

    # save user action
    db.session.add(SimulationEvent(
        simulation_id=sim.id,
        event_type="USER_ACTION",
        content=user_action
    ))

    # run fsm engine
    engine = SimulationEngine()
    step = engine.next_step(sim.state, user_action, sim.difficulty, sim.attack_type)

    # update simulation state and score
    sim.state = step["new_state"]
    attacker_message = step["attacker_message"]
    sim.risk_score += step["risk_delta"]

    # log attacker response
    db.session.add(SimulationEvent(
        simulation_id=sim.id,
        event_type="ATTACK_MESSAGE",
        content=attacker_message
    ))

    db.session.commit()

    return {
        "simulation_id": sim.id,
        "new_state": sim.state,
        "message": attacker_message,
        "risk_score": sim.risk_score
    }


# quick system health check
@main.route("/health")
def health():
    try:
        db.session.execute(text("SELECT 1"))
        return {"status": "ok"}
    except:
        return {"status": "error"}, 500


# return final simulation result
@main.route("/results/<int:simulation_id>", methods=["GET"])
def results(simulation_id):
    sim = Simulation.query.get(simulation_id)

    if not sim:
        return {"error": "Simulation not found"}, 404

    # basic risk score verdict
    if sim.risk_score >= 50:
        verdict = "High risk - user likely compromised"
    elif sim.risk_score >= 20:
        verdict = "Medium risk - user showed risky behaviour"
    else:
        verdict = "Low risk - good defensive behaviour"

    return {
        "simulation_id": sim.id,
        "final_state": sim.state,
        "risk_score": sim.risk_score,
        "verdict": verdict
    }


# get all events for one simulation
@main.route("/simulation/<int:simulation_id>/events", methods=["GET"])
def get_events(simulation_id):
    events = (SimulationEvent.query
              .filter_by(simulation_id=simulation_id)
              .order_by(SimulationEvent.created_at.asc())
              .all())

    return {
        "simulation_id": simulation_id,
        "events": [
            {
                "event_type": e.event_type,
                "content": e.content,
                "created_at": e.created_at.isoformat()
            }
            for e in events
        ]
    }


# register new user
@main.route("/register", methods=["POST"])
def register():
    data = request.get_json()

    email = data.get("email")
    password = data.get("password")

    # basic validation
    if not email or not password:
        return {"error": "Email and password required"}, 400

    # check if email already exists
    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        return {"error": "User already exists"}, 400

    # create user and hash password
    user = User(email=email)
    user.set_password(password)

    db.session.add(user)
    db.session.commit()

    return {"message": "User registered successfully"}


# login user
@main.route("/login", methods=["POST"])
def login():
    data = request.get_json()

    email = data.get("email")
    password = data.get("password")

    # find user by email
    user = User.query.filter_by(email=email).first()

    # check password
    if not user or not user.check_password(password):
        return {"error": "Invalid credentials"}, 401

    return {"message": "Login successful", "user_id": user.id}