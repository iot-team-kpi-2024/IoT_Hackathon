CREATE TABLE processed_agent_data (
    id SERIAL PRIMARY KEY,
    road_state VARCHAR(255) NOT NULL,
    humidex_state VARCHAR(255) NOT NULL,
    wind_chill_state VARCHAR(255) NOT NULL,
    user_id INTEGER NOT NULL,
    x FLOAT,
    y FLOAT,
    z FLOAT,
    latitude FLOAT,
    longitude FLOAT,
    temperature FLOAT,
    humidity FLOAT,
    speed FLOAT,
    direction FLOAT,
    timestamp TIMESTAMP
);