from aiogram.fsm.state import State, StatesGroup
class UserRegistration(StatesGroup):
    select_type = State()
    # Renter states
    renter_fullname = State()
    renter_phone = State()
    # Landlord states
    landlord_fullname = State()
    landlord_phone = State()
    landlord_company = State()
class ApartmentFilter(StatesGroup):
    district = State()
    min_price = State()
    max_price = State()
    rooms = State()

class AddApartment(StatesGroup):
    district = State()
    address = State()
    rooms = State()
    floor = State()
    total_floors = State()
    price = State()
    area = State()
    description = State()
    has_furniture = State()
    photos = State()    