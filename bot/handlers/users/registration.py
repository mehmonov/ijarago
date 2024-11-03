from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from aiogram.exceptions import TelegramBadRequest

from utils.validators import validate_phone
from states.user_states import UserRegistration
from keyboards.default.main_keyboards import (
    user_type_keyboard, 
    main_renter_keyboard, 
    main_landlord_keyboard,
    phone_number_keyboard
)

router = Router()

@router.message(UserRegistration.renter_phone)
async def process_renter_phone(message: types.Message, state: FSMContext):
    phone = validate_phone(message.text)
    if not phone:
        await message.answer(
            "❌ Noto'g'ri telefon raqam formati. Iltimos, qaytadan kiriting.\n"
            "Masalan: +998901234567",
            reply_markup=phone_number_keyboard
        )
        return
    
    try:
        data = await state.get_data()
        user = await db.add_user(
            telegram_id=message.from_user.id,
            full_name=data['full_name'],
            username=message.from_user.username,
            user_type='renter',
            phone=phone
        )
        
        await message.answer(
            "✅ Tabriklaymiz! Siz muvaffaqiyatli ro'yxatdan o'tdingiz!",
            reply_markup=main_renter_keyboard
        )
        await state.clear()
        
    except Exception as e:
        await message.answer(
            "❌ Xatolik yuz berdi. Iltimos, qaytadan urinib ko'ring.",
            reply_markup=types.ReplyKeyboardRemove()
        )
        await state.clear()