from app.entities.agent_data import AgentData
from app.entities.processed_agent_data import ProcessedAgentData

from scipy.signal import find_peaks
import numpy as np

def process_agent_data(
    agent_data: AgentData,
) -> ProcessedAgentData:
    """
    Process agent data and classify the state of the road surface.
    Parameters:
        agent_data (AgentData): Agent data that containing accelerometer, GPS, and timestamp.
    Returns:
        processed_data_batch (ProcessedAgentData): Processed data containing the classified state of the road surface and agent data.
    """
    road_state: str = "normal"

    value = agent_data.accelerometer.z

    if value <= 15000:
        road_state = "pothole"
    elif value >= 17000:
        road_state = "bump"

    # humidex
    humidex_state = "normal"
    e = 6.112 * 10.0 ** (7.5 * agent_data.humidex.temperature / (237.7 + agent_data.humidex.temperature)) * agent_data.humidex.humidity / 100.0
    humidex = agent_data.humidex.temperature + 5.0 / 9.0 * (e - 10)

    if humidex > 45:
        humidex_state = "dangerous"
    elif humidex > 40:
        humidex_state = "great discomfort"
    elif humidex > 30:
        humidex_state = "some discomfort"
    elif humidex > 20:
        humidex_state = "comfortable"
    else:
        humidex_state = "undefined"

    wind_chill_state = "some"

    return ProcessedAgentData(road_state=road_state, humidex_state=humidex_state, wind_chill_state=wind_chill_state, agent_data=agent_data)

def process_agent_data_batch(
    agent_data_list: list[AgentData],
) -> list[ProcessedAgentData]:
    processed_agent_data_list = [ProcessedAgentData(road_state="normal", humidex_state="normal", wind_chill_state="normal", agent_data=agent_data) for agent_data in agent_data_list]

    # accelerometer
    z_values = np.array([item.agent_data.accelerometer.z for item in processed_agent_data_list])
    maximum = find_peaks(z_values, height=17000, distance=10, prominence=1000, width=10)
    minimum = find_peaks(-z_values, height=-15000, distance=15, prominence=1000, width=15)

    for idx in maximum[0]:
        processed_agent_data_list[idx].road_state = "bump"

    for idx in minimum[0]:
        processed_agent_data_list[idx].road_state = "pothole"

    # humidex
    for data in processed_agent_data_list:

        e = 6.112 * 10.0 ** (7.5 * data.agent_data.humidex.temperature / (237.7 + data.agent_data.humidex.temperature)) * data.agent_data.humidex.humidity / 100.0
        humidex = data.agent_data.humidex.temperature + 5.0 / 9.0 * (e - 10)

        if humidex > 45:
            data.humidex_state = "dangerous"
        elif humidex > 40:
            data.humidex_state = "great discomfort"
        elif humidex > 30:
            data.humidex_state = "some discomfort"
        elif humidex > 20:
            data.humidex_state = "comfortable"
        else:
            data.humidex_state = "undefined"

    # wind
    speeds = np.array([item.agent_data.anemometer.speed for item in processed_agent_data_list])
    maximum = find_peaks(speeds, height=25, distance=10)

    for idx in maximum[0]:
        temperature = processed_agent_data_list[idx].agent_data.humidex.temperature
        speed_km_p_h = processed_agent_data_list[idx].agent_data.anemometer.speed * 3600 / 1000
        wind_chill = 13.12 + 0.6215 * temperature - 11.37 * speed_km_p_h ** 0.16 + 0.3965 * temperature * speed_km_p_h ** 0.16
        processed_agent_data_list[idx].wind_chill_state = "strong chill wind" if wind_chill < -10 else "strong wind"

    return processed_agent_data_list