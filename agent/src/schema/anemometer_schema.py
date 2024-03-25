from marshmallow import Schema, fields


class AnemometerSchema(Schema):
    speed = fields.Number()
    direction = fields.Number()