from aiogram import Router, F, types
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.enums.parse_mode import ParseMode

from loader import db, bot
from states.user_states import UserRegistration
from keyboards.default.main_keyboards import (
    user_type_keyboard, 
    main_renter_keyboard, 
    main_landlord_keyboard,
    phone_number_keyboard,
    profile_keyboard,
    change_role_keyboard
)
from utils.validators import validate_phone

router = Router()

@router.message(CommandStart())
async def do_start(message: types.Message, state: FSMContext):
    # Start history ga saqlash
    try:
        await db.add_start_history(
            telegram_id=message.from_user.id,
            full_name=message.from_user.full_name,
            username=message.from_user.username
        )
    except Exception as e:
        print(f"Error saving start history: {e}")

    user = await db.get_user_by_telegram_id(message.from_user.id)
    
    if user:
        keyboard = main_renter_keyboard if user['user_type'] == 'renter' else main_landlord_keyboard
        
        text = (
            f"Xush kelibsiz, {user['full_name']}!\n\n"
            f"{'Siz kvartira izlovchi sifatida' if user['user_type'] == 'renter' else 'Siz kvartira beruvchi sifatida'} "
            f"ro'yxatdan o'tgansiz."
        )
        
        await message.answer(text, reply_markup=keyboard)
        return

    await message.answer(
        "Assalomu alaykum! Botimizga xush kelibsiz!\n"
        "Iltimos, o'zingizga mos variantni tanlang:",
        reply_markup=user_type_keyboard
    )
    await state.set_state(UserRegistration.select_type)

@router.callback_query(F.data.startswith("type:"))
async def process_user_type(callback: types.CallbackQuery, state: FSMContext):
    user_type = callback.data.split(":")[1]
    await state.update_data(user_type=user_type)
    
    await callback.message.answer(
        "Iltimos, to'liq ismingizni kiriting (Familiya Ism):"
    )
    
    if user_type == "renter":
        await state.set_state(UserRegistration.renter_fullname)
    else:
        await state.set_state(UserRegistration.landlord_fullname)
    
    await callback.answer()

# Renter handlers
@router.message(UserRegistration.renter_fullname)
async def process_renter_name(message: types.Message, state: FSMContext):
    if len(message.text.split()) < 2:
        await message.answer("Iltimos, to'liq ismingizni kiriting (Familiya Ism):")
        return
    
    await state.update_data(full_name=message.text)
    await message.answer(
        "Telefon raqamingizni kiriting:\n"
        "Masalan: +998901234567",
        reply_markup=phone_number_keyboard
    )
    await state.set_state(UserRegistration.renter_phone)

@router.message(UserRegistration.renter_phone)
async def process_renter_phone(message: types.Message, state: FSMContext):
    phone = message.text
    if message.contact:
        phone = message.contact.phone_number
        if not phone.startswith('+'):
            phone = '+' + phone
            
    validated_phone = validate_phone(phone)
    if not validated_phone:
        await message.answer(
            "❌ Noto'g'ri telefon raqam formati. Iltimos, qaytadan kiriting.\n"
            "Masalan: +998901234567",
            reply_markup=phone_number_keyboard
        )
        return
    
    data = await state.get_data()
    try:
        user = await db.add_user(
            telegram_id=message.from_user.id,
            full_name=data['full_name'],
            username=message.from_user.username,
            user_type='renter',
            phone=validated_phone
        )
        
        await message.answer(
            "✅ Tabriklaymiz! Siz muvaffaqiyatli ro'yxatdan o'tdingiz!\n\n"
            "Endi siz kvartiralarni ko'rish va filter orqali qidirish imkoniyatiga egasiz.",
            reply_markup=main_renter_keyboard
        )
    except Exception as e:
        print(e)
        await message.answer(
            "❌ Xatolik yuz berdi. Iltimos, qaytadan urinib ko'ring.",
            reply_markup=types.ReplyKeyboardRemove()
        )
    
    await state.clear()

# Landlord handlers
@router.message(UserRegistration.landlord_fullname)
async def process_landlord_name(message: types.Message, state: FSMContext):
    if len(message.text.split()) < 2:
        await message.answer("Iltimos, to'liq ismingizni kiriting (Familiya Ism):")
        return
    
    await state.update_data(full_name=message.text)
    await message.answer(
        "Telefon raqamingizni kiriting:\n"
        "Masalan: +998901234567",
        reply_markup=phone_number_keyboard
    )
    await state.set_state(UserRegistration.landlord_phone)

@router.message(UserRegistration.landlord_phone)
async def process_landlord_phone(message: types.Message, state: FSMContext):
    if message.contact:
        phone = message.contact.phone_number
        if not phone.startswith('+'):
            phone = '+' + phone
    else:
        phone = message.text

    validated_phone = validate_phone(phone)
    if not validated_phone:
        await message.answer(
            "❌ Noto'g'ri telefon raqam formati. Iltimos, qaytadan kiriting.\n"
            "Masalan: +998901234567",
            reply_markup=phone_number_keyboard
        )
        return
    
    await state.update_data(phone=validated_phone)
    await message.answer(
        "Kompaniya nomini kiriting (agar mavjud bo'lsa).\n"
        "Agar yo'q bo'lsa, \"yo'q\" deb yozing:"
    )
    await state.set_state(UserRegistration.landlord_company)

@router.message(UserRegistration.landlord_company)
async def process_landlord_company(message: types.Message, state: FSMContext):
    data = await state.get_data()
    company = None if message.text.lower() in ["yo'q", "йук"] else message.text
    
    try:
        if data.get('changing_role'):
            # Rol o'zgartirish uchun
            user = await db.update_user_type(
                telegram_id=message.from_user.id,
                user_type='landlord',
                company=company
            )
            success_message = "✅ Rolingiz muvaffaqiyatli o'zgartirildi!"
        else:
            # Yangi ro'yxatdan o'tish uchun
            user = await db.add_user(
                telegram_id=message.from_user.id,
                full_name=data['full_name'],
                username=message.from_user.username,
                user_type='landlord',
                phone=data['phone'],
                company=company
            )
            success_message = (
                "✅ Tabriklaymiz! Siz muvaffaqiyatli ro'yxatdan o'tdingiz!\n\n"
                "Endi siz kvartira e'lonlarini joylash imkoniyatiga egasiz."
            )
        
        await message.answer(success_message, reply_markup=main_landlord_keyboard)
        
    except Exception as e:
        await message.answer(
            "❌ Xatolik yuz berdi. Iltimos, qaytadan urinib ko'ring.",
            reply_markup=types.ReplyKeyboardRemove()
        )
    
    await state.clear()

@router.callback_query(F.data == "close")
async def close_callback(callback: types.CallbackQuery):
    await callback.message.delete()
    await callback.answer()

@router.message(F.text == "👤 Profil")
async def show_profile(message: types.Message):
    user = await db.get_user_by_telegram_id(message.from_user.id)
    if not user:
        await message.answer("❌ Siz ro'yxatdan o'tmagansiz.")
        return
    
    user_type_text = "Kvartira izlovchi" if user['user_type'] == 'renter' else "Kvartira beruvchi"
    
    text = (
        f"👤 <b>Profil ma'lumotlari:</b>\n\n"
        f"<b>To'liq ism:</b> {user['full_name']}\n"
        f"<b>Telefon:</b> {user['phone']}\n"
        f"<b>Rol:</b> {user_type_text}\n"
    )
    
    if user['company']:
        text += f"<b>Kompaniya:</b> {user['company']}\n"
    
    await message.answer(text, reply_markup=profile_keyboard, parse_mode="HTML")

@router.message(F.text == "🔄 Rolni o'zgartirish")
async def change_role_request(message: types.Message):
    user = await db.get_user_by_telegram_id(message.from_user.id)
    if not user:
        await message.answer("❌ Siz ro'yxatdan o'tmagansiz.")
        return
    
    current_role = "Kvartira izlovchi" if user['user_type'] == 'renter' else "Kvartira beruvchi"
    
    await message.answer(
        f"Sizning hozirgi rolingiz: {current_role}\n\n"
        "Yangi rolni tanlang:",
        reply_markup=change_role_keyboard
    )

@router.callback_query(F.data.startswith("change_role:"))
async def process_role_change(callback: types.CallbackQuery, state: FSMContext):
    new_role = callback.data.split(":")[1]
    user = await db.get_user_by_telegram_id(callback.from_user.id)
    
    if user['user_type'] == new_role:
        await callback.answer("❗️ Siz allaqachon bu roldasz!", show_alert=True)
        return
    
    try:
        # Rolni o'zgartirish
        if new_role == 'landlord':
            # Rieltor uchun qo'shimcha ma'lumot so'rash
            await callback.message.answer(
                "Kompaniya nomini kiriting (agar mavjud bo'lsa).\n"
                "Agar yo'q bo'lsa, \"yo'q\" deb yozing:"
            )
            await state.set_state(UserRegistration.landlord_company)
            await state.update_data(
                changing_role=True,
                user_type=new_role,
                full_name=user['full_name'],
                phone=user['phone']
            )
        else:
            # Oddiy foydalanuvchi uchun to'g'ridan-to'g'ri o'zgartirish
            updated_user = await db.update_user_type(
                telegram_id=callback.from_user.id,
                user_type=new_role,
                company=None
            )
            
            keyboard = main_renter_keyboard if new_role == 'renter' else main_landlord_keyboard
            await callback.message.answer(
                "✅ Rolingiz muvaffaqiyatli o'zgartirildi!",
                reply_markup=keyboard
            )
    
    except Exception as e:
        await callback.message.answer("❌ Xatolik yuz berdi. Iltimos, qaytadan urinib ko'ring.")
    
    await callback.answer()

@router.message(F.text == "⬅️ Orqaga")
async def go_back_to_main(message: types.Message):
    user = await db.get_user_by_telegram_id(message.from_user.id)
    if not user:
        await message.answer("❌ Siz ro'yxatdan o'tmagansiz.")
        return
    
    keyboard = main_renter_keyboard if user['user_type'] == 'renter' else main_landlord_keyboard
    await message.answer("Asosiy menyu:", reply_markup=keyboard)