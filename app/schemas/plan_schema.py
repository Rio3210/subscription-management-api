from marshmallow import Schema, fields, validate

class PlanCreateSchema(Schema):
    name = fields.Str(required=True, validate=validate.Length(min=1, max=50))
    price = fields.Float(required=True, validate=validate.Range(min=0))
    duration_days = fields.Int(required=True, validate=validate.Range(min=1))
    features = fields.Dict(keys=fields.Str(), values=fields.Str(), required=False)

class PlanResponseSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str()
    price = fields.Float()
    duration_days = fields.Int()
    features = fields.Dict(keys=fields.Str(), values=fields.Str())
    created_at = fields.DateTime(dump_only=True) 