import sys
import os
from pathlib import Path

# Add project root to Python path
sys.path.append(str(Path(__file__).parent.parent))

from fastapi import FastAPI, HTTPException
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

from utils.db.models.users import UserQueries
from utils.db.models.apartments import ApartmentQueries
from utils.db.models.photos import PhotoQueries
from utils.db.models.filters import FilterQueries

app = FastAPI()

# Database connection
user_db = UserQueries()
apartment_db = ApartmentQueries()
photo_db = PhotoQueries()
filter_db = FilterQueries()

@app.on_event("startup")
async def startup():
    # Bu yerda o'zingizning database ma'lumotlaringizni kiriting
    for db in [user_db, apartment_db, photo_db, filter_db]:
        await db.create_pool(
            user='ijarago',
            password='1234',
            database='database_ijarago',
            host='localhost'
        )


# Pydantic modellar
class UserBase(BaseModel):
    full_name: str
    username: Optional[str] = None
    telegram_id: int
    user_type: str
    phone: Optional[str] = None
    company: Optional[str] = None
    created_at: Optional[datetime] = None
    id: Optional[int] = None

    class Config:
        from_attributes = True

class User(UserBase):
    pass

class ApartmentBase(BaseModel):
    district: str
    address: str
    rooms: int
    floor: int
    total_floors: int
    price: float
    area: float
    description: Optional[str] = None
    has_furniture: bool = False
    created_at: Optional[datetime] = None
    is_available: bool = True
    owner_name: Optional[str] = None
    owner_username: Optional[str] = None
    id: Optional[int] = None
    owner_id: Optional[int] = None

    class Config:
        from_attributes = True

class Apartment(ApartmentBase):
    pass

@app.get("/users/", response_model=List[User])
async def get_users():
    return await user_db.get_all_users()

@app.get("/users/{telegram_id}", response_model=User)
async def get_user(telegram_id: int):
    user = await user_db.get_user_by_telegram_id(telegram_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.post("/users/", response_model=User)
async def create_user(user: UserBase):
    return await user_db.add_user(
        telegram_id=user.telegram_id,
        full_name=user.full_name,
        username=user.username,
        user_type=user.user_type,
        phone=user.phone,
        company=user.company
    )

@app.put("/users/{telegram_id}/type", response_model=User)
async def update_user_type(telegram_id: int, user_type: str):
    user = await user_db.update_user_type(telegram_id, user_type)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

# Apartments endpointlari
@app.get("/apartments/", response_model=List[Apartment])
async def get_apartments(
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    district: Optional[str] = None,
    min_rooms: Optional[int] = None,
    max_rooms: Optional[int] = None
):
    return await apartment_db.get_apartments_by_filters(
        min_price=min_price,
        max_price=max_price,
        district=district,
        min_rooms=min_rooms,
        max_rooms=max_rooms
    )

@app.get("/apartments/{apartment_id}", response_model=Apartment)
async def get_apartment(apartment_id: int):
    apartment = await apartment_db.get_apartment_by_id(apartment_id)
    if not apartment:
        raise HTTPException(status_code=404, detail="Apartment not found")
    return apartment

@app.post("/apartments/", response_model=Apartment)
async def create_apartment(apartment: ApartmentBase, owner_id: int):
    return await apartment_db.add_apartment(
        owner_id=owner_id,
        district=apartment.district,
        address=apartment.address,
        rooms=apartment.rooms,
        floor=apartment.floor,
        total_floors=apartment.total_floors,
        price=apartment.price,
        area=apartment.area,
        description=apartment.description,
        has_furniture=apartment.has_furniture
    )

@app.put("/apartments/{apartment_id}/status")
async def update_apartment_status(apartment_id: int, is_available: bool):
    apartment = await apartment_db.update_apartment_status(apartment_id, is_available)
    if not apartment:
        raise HTTPException(status_code=404, detail="Apartment not found")
    return apartment

@app.delete("/apartments/{apartment_id}")
async def delete_apartment(apartment_id: int):
    result = await db.delete_apartment(apartment_id)
    if not result:
        raise HTTPException(status_code=404, detail="Apartment not found")
    return {"message": "Apartment deleted successfully"}