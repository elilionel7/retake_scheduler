from flask import Blueprint, render_template
from app.extensions import cache

home_bp = Blueprint('home-bp', __name__)

@home_bp.route('/')
@cache.cached(timeout=60)
def home():
    return render_template('home.html')
