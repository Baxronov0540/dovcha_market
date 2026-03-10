from pydantic import BaseModel


class LocationCreateResponse(BaseModel):
    id: int
    region_id: int
    district: str
    house: str
    postal_code: str
    latitude: float
    longitude: float
    phone: str
    working_hours: str
    is_active: bool
