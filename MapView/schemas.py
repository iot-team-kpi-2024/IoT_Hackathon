from dataclasses import dataclass
from datetime import datetime

@dataclass
class Accelerometer:
    X: int
    Y: int
    Z: int

@dataclass
class Gps:
    longitude: float
    latitude: float
    
@dataclass
class Humidex:
    temperature: float
    humidity: float

@dataclass
class AggregatedData:
    accelerometer: Accelerometer
    gps: Gps
    humidex: Humidex
    time: datetime


from marshmallow import Schema, fields

class AccelerometerSchema(Schema):
    X = fields.Int()
    Y = fields.Int()
    Z = fields.Int()

class GpsSchema(Schema):
    longitude = fields.Number()
    latitude = fields.Number()

class HumidexSchema(Schema):
    temperature = fields.Number()
    humidity = fields.Number()


from pydantic import BaseModel, field_validator
from datetime import datetime

class AccelerometerData(BaseModel):
    x: float
    y: float
    z: float

class GpsData(BaseModel):
    latitude: float
    longitude: float

class HumidexData(BaseModel):
    temperature: float
    humidity: float

class AnemometerData(BaseModel):
    speed: float
    direction: float

class AgentData(BaseModel):
    user_id: int
    accelerometer: AccelerometerData
    gps: GpsData
    humidex: HumidexData
    anemometer: AnemometerData
    timestamp: datetime

    @classmethod
    @field_validator("timestamp", mode="before")
    def check_timestamp(cls, value):
        if isinstance(value, datetime):
            return value
        try:
            return datetime.fromisoformat(value)
        except (TypeError, ValueError):
            raise ValueError(
                "Invalid timestamp format. Expected ISO 8601 format (YYYY-MM-DDTHH:MM:SSZ)."
            )

class ProcessedAgentData(BaseModel):
    road_state: str
    humidex_state: str
    wind_chill_state: str
    agent_data: AgentData