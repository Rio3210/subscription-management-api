from marshmallow import Schema, fields, validate

class UserCreateSchema(Schema):
    email = fields.Email(required=True)
    password = fields.Str(required=True, validate=validate.Length(min=6))

class UserResponseSchema(Schema):
    id = fields.Int(dump_only=True)
    email = fields.Email()
    created_at = fields.DateTime(dump_only=True)

class UserLoginSchema(Schema):
    email = fields.Email(required=True)
    password = fields.Str(required=True) 