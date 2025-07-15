from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton


main_menu_button = KeyboardButton(text="🏠 Asosiy Menyu")


def get_district_keyboard() -> ReplyKeyboardMarkup:
    districts = [
        "Chilonzor", "Yunusobod", "Mirzo Ulug'bek", 
        "Yakkasaroy", "Mirobod", "Sergeli", 
        "Olmazor", "Uchtepa", "Shayxontohur"
    ]
    
    keyboard = []
    for i in range(0, len(districts), 3):
        row = districts[i:i+3]
        keyboard.append([KeyboardButton(text=district) for district in row])
    keyboard.append([main_menu_button])
    
    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True
    )
user_type_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="🏠 Kvartira izlayapman", callback_data="type:renter"),
            InlineKeyboardButton(text="🏢 Kvartira ijaraga beraman", callback_data="type:landlord")
        ]
    ]
)

phone_number_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📱 Telefon raqamni yuborish", request_contact=True)],
        [main_menu_button]
    ],
    resize_keyboard=True
)

main_renter_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="🏠 Kvartiralarni ko'rish"),
            KeyboardButton(text="🔍 Filter o'rnatish")
        ],
        [
            KeyboardButton(text="⭐️ Saqlangan filterlar"),
            KeyboardButton(text="👤 Profil")
        ],
        [main_menu_button]
    ],
    resize_keyboard=True
)

main_landlord_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="➕ Kvartira qo'shish"),
            KeyboardButton(text="📋 Mening e'lonlarim")
        ],
        [
            KeyboardButton(text="👤 Profil")
        ],
        [main_menu_button]
    ],
    resize_keyboard=True
)

furniture_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="✅ Ha"),
            KeyboardButton(text="❌ Yo'q")
        ],
        [main_menu_button]
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)

confirm_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="✅ Yakunlash")],
        [main_menu_button]
    ],
    resize_keyboard=True
)


profile_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="🔄 Rolni o'zgartirish"),
            KeyboardButton(text="✏️ Ma'lumotlarni tahrirlash")
        ],
        [
            KeyboardButton(text="⬅️ Orqaga")
        ],
        [main_menu_button]
    ],
    resize_keyboard=True
)

change_role_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="🏠 Kvartira izlovchi", 
                callback_data="change_role:renter"
            ),
            InlineKeyboardButton(
                text="🏢 Kvartira beruvchi", 
                callback_data="change_role:landlord"
            )
        ]
    ]
)