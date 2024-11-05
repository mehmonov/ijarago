from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

def get_apartment_keyboard(apartment_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="📞 Bog'lanish", callback_data=f"contact:{apartment_id}"),
        InlineKeyboardButton(text="📍 Lokatsiya", callback_data=f"location:{apartment_id}")
    )
    builder.row(InlineKeyboardButton(text="❌ Yopish", callback_data="close"))
    return builder.as_markup()

def get_district_keyboard() -> InlineKeyboardMarkup:
    districts = [
        "Chilonzor", "Yunusobod", "Mirzo Ulug'bek", 
        "Yakkasaroy", "Mirobod", "Sergeli", 
        "Olmazor", "Uchtepa", "Shayxontohur"
    ]
    
    builder = InlineKeyboardBuilder()
    for district in districts:
        builder.button(text=district, callback_data=f"district:{district}")
    builder.adjust(3)
    return builder.as_markup()

def create_apartment_keyboard(apartment_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="📞 Bog'lanish", callback_data=f"contact:{apartment_id}")
    builder.button(text="📍 Lokatsiya", callback_data=f"location:{apartment_id}")
    builder.adjust(1)
    return builder.as_markup()