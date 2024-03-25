from schema.gps_schema import GpsSchema
from marshmallow import Schema, fields

class HumidexSchema(Schema):
    temperature = fields.Number()
    humidity = fields.Number()