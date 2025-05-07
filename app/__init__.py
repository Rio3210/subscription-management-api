from flask import Flask
from flask_jwt_extended import JWTManager
from app.core.config import config
from app.core.database import init_db
from app.models import User
from app.core.database import db

def create_app(config_name):
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    jwt = JWTManager(app)
    init_db(app)
    
    # Initialize API
    from app.api import api
    api.init_app(app)
    
    # Register blueprints
    from app.api import auth_bp, plans_bp, subscriptions_bp, users_bp
    app.register_blueprint(subscriptions_bp, url_prefix='/subscriptions')
    app.register_blueprint(plans_bp, url_prefix='/plans')
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(users_bp, url_prefix='/users')
    
    return app 