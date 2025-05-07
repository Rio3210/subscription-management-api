from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_restx import Namespace, Resource, fields
from app.services.subscription_service import SubscriptionService
from app.schemas.subscription_schema import (
    SubscriptionCreateSchema, 
    SubscriptionResponseSchema, 
    SubscriptionHistoryResponseSchema,
    SubscriptionHistoryGroupedResponseSchema
)
from marshmallow import ValidationError
from app.api.plans import plan_model
from app.models.subscription import SubscriptionStatus
from itertools import groupby


subscriptions_bp = Blueprint('subscriptions', __name__)
subscriptions_ns = Namespace(
    'subscriptions',
    description='Subscription operations',
    security='Bearer Auth'
)


subscription_service = SubscriptionService()
subscription_schema = SubscriptionResponseSchema()


subscription_model = subscriptions_ns.model('Subscription', {
    'id': fields.Integer(readonly=True),
    'user_id': fields.Integer(readonly=True),
    'plan_id': fields.Integer(required=True, description='Plan ID'),
    'status': fields.String(description='Subscription status'),
    'start_date': fields.DateTime(readonly=True),
    'end_date': fields.DateTime(readonly=True),
    'created_at': fields.DateTime(readonly=True),
    'plan': fields.Nested(plan_model)
})

subscription_create_model = subscriptions_ns.model('SubscriptionCreate', {
    'plan_id': fields.Integer(required=True, description='Plan ID')
})

@subscriptions_ns.route('/')
@subscriptions_ns.doc(security='Bearer Auth')
class SubscriptionList(Resource):
    @subscriptions_ns.doc('list_subscriptions')
    @subscriptions_ns.marshal_list_with(subscription_model)
    @jwt_required()
    def get(self):
        current_user_id = get_jwt_identity()
        subscriptions = subscription_service.get_user_subscriptions(current_user_id)
        print(subscriptions, 'here subscription')
        return [subscription_schema.dump(sub) for sub in subscriptions]

    @subscriptions_ns.doc('create_subscription')
    @subscriptions_ns.expect(subscription_create_model)
    @subscriptions_ns.marshal_with(subscription_model, code=201)
    @jwt_required()
    def post(self):
        try:
            current_user_id = get_jwt_identity()
            data = SubscriptionCreateSchema().load(request.get_json())
            subscription = subscription_service.create_subscription(
                user_id=current_user_id,
                plan_id=data['plan_id']
            )
            return subscription_schema.dump(subscription), 201
        except ValidationError as err:
            subscriptions_ns.abort(400, error=err.messages)
        except ValueError as err:
            subscriptions_ns.abort(400, error=str(err))

@subscriptions_ns.route('/status/<string:status>')
@subscriptions_ns.param('status', 'Subscription status (active, cancelled, expired)')
@subscriptions_ns.doc(security='Bearer Auth')
class SubscriptionByStatus(Resource):
    @subscriptions_ns.doc('get_subscriptions_by_status')
    @subscriptions_ns.marshal_list_with(subscription_model)
    @jwt_required()
    def get(self, status):
        try:
            # Validate status
            if status not in [s.value for s in SubscriptionStatus]:
                subscriptions_ns.abort(400, error=f"Invalid status. Must be one of: {[s.value for s in SubscriptionStatus]}")
            
            subscriptions = subscription_service.get_subscriptions_by_status(status)
            return subscriptions
        except ValueError as err:
            subscriptions_ns.abort(400, error=str(err))

@subscriptions_ns.route('/<int:subscription_id>')
@subscriptions_ns.param('subscription_id', 'Subscription id')
@subscriptions_ns.doc(security='Bearer Auth')
class Subscription(Resource):
    @subscriptions_ns.doc('get_subscription')
    @subscriptions_ns.marshal_with(subscription_model)
    @jwt_required()
    def get(self, subscription_id):
        subscription = subscription_service.get_subscription_by_id(subscription_id)
        if not subscription:
            subscriptions_ns.abort(404, error="Subscription not found")
        return subscription_schema.dump(subscription)
    
    @subscriptions_ns.doc('update_subscription')
    @subscriptions_ns.expect(subscription_model)
    @subscriptions_ns.marshal_with(subscription_model)
    @jwt_required()
    def put(self, subscription_id):
        current_user_id = get_jwt_identity()
        try:
            subscription = subscription_service.update_subscription(
                subscription_id=subscription_id,
                user_id=current_user_id,
                status=request.json.get('status'),
                plan_id=request.json.get('plan_id')
            )
            return subscription_schema.dump(subscription)
        except ValueError as err:
            subscriptions_ns.abort(404, error=str(err))

    @subscriptions_ns.doc('cancel_subscription')
    @subscriptions_ns.response(200, 'Subscription cancelled')
    @jwt_required()
    def delete(self, subscription_id):
        current_user_id = get_jwt_identity()
        try:
            subscription_service.cancel_subscription(subscription_id, current_user_id)
            return {'message': 'Subscription cancelled successfully'}
        except ValueError as err:
            subscriptions_ns.abort(404, error=str(err))

@subscriptions_ns.route('/history')
@subscriptions_ns.doc(security='Bearer Auth')
class SubscriptionHistoryList(Resource):
    @jwt_required()
    @subscriptions_ns.doc('get_all_user_subscription_history')
    def get(self):
        current_user_id = get_jwt_identity()
        service = SubscriptionService()
        # Get pre-grouped history entries
        grouped_history = service.get_all_user_subscription_history(user_id=current_user_id)
        
        if not grouped_history:
            return {'message': 'No subscription history found'}, 404

        # Serialize each group of entries
        serialized_history = {
            str(sub_id): SubscriptionHistoryResponseSchema(many=True).dump(entries)
            for sub_id, entries in grouped_history.items()
        }
        
        return {'subscriptions': serialized_history}

@subscriptions_ns.route('/history/<int:subscription_id>')
@subscriptions_ns.doc(security='Bearer Auth')
@subscriptions_ns.param('subscription_id', 'The subscription ID')
class SubscriptionHistoryDetail(Resource):
    @jwt_required()
    @subscriptions_ns.doc('get_subscription_history')
    def get(self, subscription_id):
        current_user_id = get_jwt_identity()
        service = SubscriptionService()

        subscription = service.get_subscription_by_id(subscription_id)
        if not subscription or subscription.user_id != int(current_user_id):
            return {'message': 'Subscription not found'}, 404
        
        history_entries = service.get_subscription_history_by_id(subscription_id)
        
        if not history_entries:
            return {'message': 'No history found for this subscription'}, 404
            
        return SubscriptionHistoryResponseSchema(many=True).dump(history_entries) 