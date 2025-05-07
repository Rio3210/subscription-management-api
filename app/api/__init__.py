from flask_restx import Api
from app.api.auth import auth_bp, auth_ns
from app.api.plans import plans_bp, plans_ns
from app.api.subscriptions import subscriptions_bp, subscriptions_ns
from app.api.users import users_bp, users_ns


authorizations = {
    'Bearer Auth': {
        'type': 'apiKey',
        'in': 'header',
        'name': 'Authorization',
        'description': 'Add "Bearer <JWT token>" to authorize'
    }
}

api = Api(
    title='Subscription Management API',
    version='1.0',
    description='A RESTful API for managing user subscriptions',
    doc='/docs',
    authorizations=authorizations,
    security='Bearer Auth'
)


api.add_namespace(auth_ns)
api.add_namespace(plans_ns)
api.add_namespace(subscriptions_ns)
api.add_namespace(users_ns)

__all__ = ['auth_bp', 'plans_bp', 'subscriptions_bp', 'users_bp', 'api'] 