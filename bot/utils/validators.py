import re
from typing import Union


def validate_phone(phone: str) -> str | None:
  
    pattern = r'^\+998\d{9}$'
    
    if re.match(pattern, phone):
        return phone
    return None

def validate_price(price: str) -> Union[int, bool]:
    try:
        price = int(price.replace(" ", ""))
        if price <= 0:
            return False
        return price
    except ValueError:
        return False

def validate_rooms(rooms: str) -> Union[int, bool]:
    try:
        rooms = int(rooms)
        if rooms <= 0 or rooms > 10:
            return False
        return rooms
    except ValueError:
        return False

def validate_floor(floor: str, total_floors: int = None) -> Union[int, bool]:
    try:
        floor = int(floor)
        if floor <= 0:
            return False
        if total_floors and floor > total_floors:
            return False
        return floor
    except ValueError:
        return False
