from dataclasses import dataclass

from datetime import datetime
from domain.accelerometer import Accelerometer
from domain.gps import Gps
from domain.humidex import Humidex
from domain.anemometer import Anemometer

@dataclass
class AggregatedData:
    accelerometer: Accelerometer
    gps: Gps
    humidex: Humidex
    anemometer: Anemometer
    timestamp: datetime
    user_id: int
