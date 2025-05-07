from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from flask_restx import Namespace, Resource, fields
from app.services.user_service import UserService
from marshmallow import ValidationError

users_bp = Blueprint('users', __name__)
users_ns = Namespace('users', description='User operations', security='Bearer Auth')


user_service = UserService()


user_model = users_ns.model('User', {
    'id': fields.Integer(readonly=True),
    'email': fields.String(required=True, description='User email'),
    'is_admin': fields.Boolean(description='Admin status'),
    'created_at': fields.DateTime(readonly=True),
    'subscription_count': fields.Integer(description='Number of subscriptions'),
    'last_subscription_date': fields.DateTime(description='Date of last subscription')
})

@users_ns.route('/email/<string:email>')
@users_ns.param('email', 'User email address')
@users_ns.doc(security='Bearer Auth')
class UserByEmail(Resource):
    @users_ns.doc('get_user_by_email')
    @users_ns.marshal_with(user_model)
    @jwt_required()
    def get(self, email):
        try:
            user = user_service.get_user_by_email(email)
            if not user:
                users_ns.abort(404, error="User not found")
            return user
        except ValueError as err:
            users_ns.abort(400, error=str(err)) 