from pydantic import BaseModel
from app.entities.agent_data import AgentData


class ProcessedAgentData(BaseModel):
    road_state: str
    humidex_state: str
    wind_chill_state: str
    agent_data: AgentData
