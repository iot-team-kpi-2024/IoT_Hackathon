from marshmallow import Schema, fields
from schema.accelerometer_schema import AccelerometerSchema
from schema.gps_schema import GpsSchema
from schema.humidex_schema import HumidexSchema
from schema.anemometer_schema import AnemometerSchema


class AggregatedDataSchema(Schema):
    accelerometer = fields.Nested(AccelerometerSchema)
    gps = fields.Nested(GpsSchema)
    humidex = fields.Nested(HumidexSchema)
    anemometer = fields.Nested(AnemometerSchema)
    timestamp = fields.DateTime("iso")
    user_id = fields.Int()
