from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# Initialize SQLAlchemy
db = SQLAlchemy()

# Initialize Flask-Migrate
migrate = Migrate()

def seed_admin(app):
    from app.models import User
    with app.app_context():
        admin_email = "admin@gmail.com"
        admin_password = "Pass@123"
        admin = User.query.filter_by(email=admin_email).first()
        if not admin:
            admin = User(email=admin_email, is_admin=True)
            admin.set_password(admin_password)
            db.session.add(admin)
            db.session.commit()

def init_db(app):
    """Initialize the database with the Flask app."""
    db.init_app(app)
    migrate.init_app(app, db)
    seed_admin(app) 