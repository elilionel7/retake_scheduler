from flask_mail import Mail
from dotenv import load_dotenv
import os

# Initialize extensions
mail = Mail()

def configure_app(app):
    # Load environment variables
    load_dotenv()

    # General Flask settings
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'default-secret-key')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI', 'sqlite:///instance/scheduler.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Email configurations
    app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
    app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587))
    app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS', 'True') == 'True'
    app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME', 'your-email@example.com')
    app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD', 'your-email-password')

    # Initialize Mail extension
    mail.init_app(app)
