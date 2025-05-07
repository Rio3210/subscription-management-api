from marshmallow import Schema, fields, validate

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