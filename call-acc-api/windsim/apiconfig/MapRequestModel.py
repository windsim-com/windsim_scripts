from pydantic_settings import BaseSettings


class MapRequestModel(BaseSettings):
    maximumArea: []
    minimumArea: []

    modelArea: []

class ExtensionInPixels(BaseSettings):
    height: int
    width: int

class SimulationDomain(BaseSettings):
    coordinates: []

class Coordinate(BaseSettings):
    latitude: float
    longitude: float