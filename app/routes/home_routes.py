# app/routes/home_routes.py

from flask import Blueprint, render_template

# Create a blueprint named "home_bp"
home_bp = Blueprint('home-bp', __name__)

@home_bp.route('/')
def home():
    """Render the home.html template."""
    return render_template('home.html')
