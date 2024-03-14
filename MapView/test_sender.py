import requests
import time
import json

from file_datasource import FileDatasource
from schemas import *

def create_processed_agent_data(aggregated_data) -> ProcessedAgentData:
    return ProcessedAgentData(
        road_state="normal",
        agent_data=AgentData(
            user_id=1,
            accelerometer=AccelerometerData(
                x=aggregated_data.accelerometer.X,
                y=aggregated_data.accelerometer.Y,
                z=aggregated_data.accelerometer.Z),
            gps=GpsData(
                latitude=aggregated_data.gps.latitude,
                longitude=aggregated_data.gps.longitude),
            timestamp=aggregated_data.time
        )
    )

def process_accelerometer_data(processed_data: list[ProcessedAgentData]):
    for item in data:
        if item.accelerometer.Z > 1700:
            item.road_state = "bump"
        elif item.accelerometer.Z < 1500:
            item.road_state = "pothole"

# main
file_datasource = FileDatasource("data.csv", "gps.csv")
file_datasource.startReading()

while True:
    data = file_datasource.read(100)
    processed_data = list(map(create_processed_agent_data, data))
    
    process_accelerometer_data(processed_data)

    items_json_strings = [item.model_dump_json() for item in processed_data]
    items_dicts = [json.loads(item_json) for item_json in items_json_strings]
    response = requests.post("http://127.0.0.1:8000/processed_agent_data/", json=items_dicts)

    time.sleep(10)