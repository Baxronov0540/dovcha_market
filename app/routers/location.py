from fastapi import APIRouter, HTTPException
from geopy.geocoders import Nominatim
from sqlalchemy import select

from app.database import db_dep
from app.models import DeliveryPoint, Region
from app.dependencies import current_user_jwt_dep
from app.schemas import LocationCreateResponse

router = APIRouter(prefix="/address", tags=["Address"])

geolocator = Nominatim(user_agent="Dovcha_market")


@router.post("/delivery-point", response_model=LocationCreateResponse)
async def create_delivery_point(
    session: db_dep,
    lat: float,
    lon: float,
    phone: str,
    working_hours: str,
    current_user: current_user_jwt_dep,
):

    location_query = f"{lat}, {lon}"

    location = geolocator.reverse(location_query, language="uz")

    if not location:
        raise HTTPException(status_code=404, detail="Location not found")

    address = location.raw.get("address", {})
    district = (
        address["county"] + " " + address["neighbourhood"] + "," + address["road"]
    )
    postal_code = address["postcode"]
    region_name = address["city"]
    print(">>>>>", address)

    # district = address.get("city_district") or address.get("district")
    # region_name = address.get("state")

    if not region_name:
        raise HTTPException(status_code=400, detail="Region not found")

    stmt = select(Region).where(Region.name == region_name)
    region = session.execute(stmt).scalar_one_or_none()

    if not region:
        region = Region(name=region_name)
        session.add(region)
        session.flush()

    delivery_point = DeliveryPoint(
        region_id=region.id,
        district=district,
        house=address.get("house_number", "unknown"),
        postal_code=postal_code,
        latitude=lat,
        longitude=lon,
        phone=phone,
        working_hours=working_hours,
        is_active=True,
    )

    session.add(delivery_point)
    session.commit()
    session.refresh(delivery_point)

    return delivery_point
