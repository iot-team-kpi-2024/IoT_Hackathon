from dataclasses import dataclass


@dataclass
class Anemometer:
    speed: float # m/s
    direction: float # degree 0-360 (0 - North, clockwise)