from marshmallow import Schema, fields, validate
from app.schemas.plan_schema import PlanResponseSchema

class SubscriptionCreateSchema(Schema):
    plan_id = fields.Int(required=True)

class SubscriptionResponseSchema(Schema):
    id = fields.Int(dump_only=True)
    user_id = fields.Int(dump_only=True)
    plan_id = fields.Int()
    status = fields.Str()
    start_date = fields.DateTime()
    end_date = fields.DateTime()
    created_at = fields.DateTime(dump_only=True)
    plan = fields.Nested('PlanResponseSchema')

class SubscriptionHistoryResponseSchema(Schema):
    id = fields.Int(dump_only=True)
    subscription_id = fields.Int(required=True)
    user_id = fields.Int(required=True)
    old_plan = fields.Nested(PlanResponseSchema, allow_none=True)
    new_plan = fields.Nested(PlanResponseSchema, allow_none=True)
    old_status = fields.Str(allow_none=True)
    new_status = fields.Str(allow_none=True)
    change_type = fields.Str(required=True)
    changed_at = fields.DateTime(dump_only=True)
    subscription = fields.Nested('SubscriptionResponseSchema', only=('id', 'plan'))

class SubscriptionHistoryGroupedResponseSchema(Schema):
    subscriptions = fields.Dict(
        keys=fields.Int(),  # subscription_id
        values=fields.List(fields.Nested(SubscriptionHistoryResponseSchema))
    ) 