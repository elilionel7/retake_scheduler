from flask import Blueprint

# Create a Blueprint for home-related routes
home_bp = Blueprint('home', __name__)

@home_bp.route('/')
def home():
    return "Welcome to the Retake Scheduler App!"
