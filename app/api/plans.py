from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_restx import Namespace, Resource, fields
from app.services.plan_service import PlanService
from app.schemas.plan_schema import PlanCreateSchema, PlanResponseSchema
from marshmallow import ValidationError
from app.models import User


plans_bp = Blueprint('plans', __name__)
plans_ns = Namespace('plans', description='Subscription plan operations')


plan_service = PlanService()
plan_schema = PlanResponseSchema()


plan_model = plans_ns.model('Plan', {
    'id': fields.Integer(readonly=True),
    'name': fields.String(required=True, description='Plan name'),
    'price': fields.Float(required=True, description='Plan price'),
    'duration_days': fields.Integer(required=True, description='Plan duration in days'),
    'features': fields.Raw(description='Plan features'),
    'created_at': fields.DateTime(readonly=True)
})

@plans_ns.route('/')
class PlanList(Resource):
    @plans_ns.doc('list_plans')
    @plans_ns.marshal_list_with(plan_model)
    @jwt_required()
    def get(self):
        """List all subscription plans"""
        plans = plan_service.get_all_plans()
        return [plan_schema.dump(plan) for plan in plans]
    

    @plans_ns.doc('create_plan')
    @plans_ns.expect(plan_model)
    @plans_ns.marshal_with(plan_model, code=201)
    @jwt_required()
    def post(self):
        """Only allowed for admin"""
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        if not user or not user.is_admin:
            plans_ns.abort(403, error="Admin privileges required")
        try:
            data = PlanCreateSchema().load(request.get_json())
            plan = plan_service.create_plan(
                name=data['name'],
                price=data['price'],
                duration_days=data['duration_days'],
                features=data.get('features', {})
            )
            return plan_schema.dump(plan), 201
        except ValidationError as err:
            plans_ns.abort(400, error=err.messages)
        except ValueError as err:
            plans_ns.abort(400, error=str(err))

@plans_ns.route('/<int:plan_id>')
@plans_ns.param('plan_id', 'The plan identifier')
class Plan(Resource):
    @plans_ns.doc('get_plan')
    @plans_ns.marshal_with(plan_model)
    @jwt_required()
    def get(self, plan_id):
        plan = plan_service.get_plan_by_id(plan_id)
        if not plan:
            plans_ns.abort(404, error="Plan not found")
        return plan_schema.dump(plan)

    @plans_ns.doc('update_plan')
    @plans_ns.expect(plan_model)
    @plans_ns.marshal_with(plan_model)
    @jwt_required()
    def put(self, plan_id):
        try:
            data = request.get_json()
            plan = plan_service.update_plan(plan_id, **data)
            return plan_schema.dump(plan)
        except ValueError as err:
            plans_ns.abort(404, error=str(err))

    @plans_ns.doc('delete_plan')
    @plans_ns.response(204, 'Plan deleted')
    @jwt_required()
    def delete(self, plan_id):
        try:
            plan_service.delete_plan(plan_id)
            return '', 204
        except ValueError as err:
            plans_ns.abort(404, error=str(err)) 