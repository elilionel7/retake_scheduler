from flask import Blueprint

home_bp = Blueprint('home', __name__, url_prefix='')  # No prefix, global namespace

@home_bp.route('/')
def home():
    return "Welcome to the Retake Scheduler App!"
