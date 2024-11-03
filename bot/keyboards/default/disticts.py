from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def get_district_keyboard() -> ReplyKeyboardMarkup:
    districts = [
        "Chilonzor", "Yunusobod", "Mirzo Ulug'bek", 
        "Yakkasaroy", "Mirobod", "Sergeli", 
        "Olmazor", "Uchtepa", "Shayxontohur"
    ]
    
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    rows = []
    for i in range(0, len(districts), 3):
        row = districts[i:i+3]
        keyboard.row(*[KeyboardButton(text=district) for district in row])
    
    return keyboard