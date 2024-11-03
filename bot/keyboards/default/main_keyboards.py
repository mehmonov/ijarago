from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

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
        [KeyboardButton(text="📱 Telefon raqamni yuborish", request_contact=True)]
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
        ]
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
        ]
    ],
    resize_keyboard=True
)

furniture_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="✅ Ha"),
            KeyboardButton(text="❌ Yo'q")
        ]
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)

confirm_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="✅ Yakunlash")]
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
        ]
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