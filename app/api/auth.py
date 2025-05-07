from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from flask_restx import Namespace, Resource, fields, Api
from app.services.auth_service import AuthService
from app.schemas.user_schema import UserCreateSchema, UserResponseSchema
from marshmallow import ValidationError


auth_bp = Blueprint('auth', __name__)
auth_ns = Namespace('auth', description='Authentication operations')


auth_service = AuthService()
user_schema = UserResponseSchema()

# Define models for Swagger
user_model = auth_ns.model('User', {
    'id': fields.Integer(readonly=True),
    'email': fields.String(required=True, description='User email'),
    'created_at': fields.DateTime(readonly=True)
})

auth_response = auth_ns.model('AuthResponse', {
    'user': fields.Nested(user_model),
    'access_token': fields.String(description='JWT access token')
})

register_model = auth_ns.model('Register', {
    'email': fields.String(required=True, description='User email'),
    'password': fields.String(required=True, description='User password')
})

login_model = auth_ns.model('Login', {
    'email': fields.String(required=True, description='User email'),
    'password': fields.String(required=True, description='User password')
})

subscription_create_model = auth_ns.model('SubscriptionCreate', {
    'plan_id': fields.Integer(required=True, description='Plan ID')
})

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

@auth_ns.route('/register')
class Register(Resource):
    @auth_ns.expect(register_model)
    @auth_ns.response(201, 'User created successfully', auth_response)
    @auth_ns.response(400, 'Validation error')
    def post(self):
        """Register a new user"""
        try:
            data = UserCreateSchema().load(request.get_json())
            user, access_token = auth_service.register_user(
                email=data['email'],
                password=data['password']
            )
            return {
                'user': user_schema.dump(user),
                'access_token': access_token
            }, 201
        except ValidationError as err:
            return {'error': err.messages}, 400
        except ValueError as err:
            return {'error': str(err)}, 400

@auth_ns.route('/login')
class Login(Resource):
    @auth_ns.expect(login_model)
    @auth_ns.response(200, 'Login successful', auth_response)
    @auth_ns.response(401, 'Invalid credentials')
    def post(self):
        """Login user"""
        try:
            data = request.get_json()
            user = auth_service.authenticate_user(
                email=data['email'],
                password=data['password']
            )
            access_token = create_access_token(identity=str(user.id))
            return {
                'user': user_schema.dump(user),
                'access_token': access_token
            }, 200
        except ValueError as err:
            return {'error': str(err)}, 401 