# AI-Powered Cybersecurity Threat Simulator

My final year project is a web based system that simulates cyber attacks like phishing and social engineering. The idea is to let users interact with realistic attack scenarios and then evaluate how they respond. The system adapts based on user actions and gives a final result showing whether the user handled the situation safely or not.

---

## What the system does

- Users can register and log in
- Start a simulation
- Receive attacker messages in a chat style interface
- Choose actions like to click the link, ignore or report it
- System responds based on those actions
- A final risk score is given at the end

There are 2 different scenario like:
- IT support phishing
- Delivery scam

Difficulty can also be changed.

---

## How it works

The backend uses something called a **finite-state machine (FSM)**.

This means:
- The attack moves through different stages
- Your actions decide what happens next
- The system tracks everything and calculates risk

There is also AI using OpenAI APT, but the system works without it using predefined messages.

---

## Tech used

- Python (Flask)
- MySQL
- SQLAlchemy
- HTML / CSS / JavaScript

---

## How to run it

### Prerequisites

- Python (3.11 or newer)
- Git
- MySQL Server
- MySQL Workbench (optional but recommended)

Please make sure:
- MySQL is running
- A database called `fyp_db` can be created
- You have access to MySQL credentials

### 1. Clone the project

Open windows powershell in administrator mode and type the following:

git clone https://campus.cs.le.ac.uk/gitlab/ug_project/25-26/sm1248.git

cd sm1248

### 2. Create virtual environment

py -m venv venv

### 3. Activate it

venv\Scripts\activate
If it comes up with an error due to scripts being disabled, run this line first and try it again:
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser

### 4. Install requirements

pip install -r requirements.txt

---

## Database setup

Make sure MySQL is installed.

Open MySQL workbench, load up local instance MySQL80 and enter:

CREATE DATABASE fyp_db;


---

## Run the app

Go back to powershell and type

py run.py


Then head to any internet browser and open:

http://127.0.0.1:5000


---

## Project structure (main parts)

- `webapp/` → main application
- `simulation_engine.py` → controls attack logic
- `llmservice.py` → handles AI (optional)
- `models.py` → database models
- `routes.py` → app routes
- `templates/` → frontend pages

---

## Notes

- The system does not rely on AI to work
- If OpenAI is not available, it uses fallback messages
- This was done to keep the system reliable

---

## Author

Sagid  
Final Year Computer Science Project  
University of Leicester
