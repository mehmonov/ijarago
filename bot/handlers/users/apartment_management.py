from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from aiogram.exceptions import TelegramBadRequest
from loader import db, bot
from utils.validators import validate_price, validate_rooms, validate_floor
from states.user_states import AddApartment
from utils.apartment_utils import select_best_apartment
from aiogram.utils.keyboard import InlineKeyboardBuilder

from keyboards.default.main_keyboards import (
    confirm_keyboard,
    furniture_keyboard,
    main_landlord_keyboard,
    get_district_keyboard
)

from .apartment_listing import format_apartment_info
router = Router()

@router.message(F.text == "➕ Kvartira qo'shish")
async def start_adding_apartment(message: types.Message, state: FSMContext):
    user = await db.get_user_by_telegram_id(message.from_user.id)
    
    if not user:
        await message.answer("❌ Siz ro'yxatdan o'tmagansiz.")
        return
        
    if user['user_type'] != 'landlord':
        await message.answer("❌ Faqat kvartira beruvchilar e'lon qo'sha oladi.")
        return
    
    i_btn = get_district_keyboard()
    await message.answer("Kvartira joylashgan tumanni tanlang:", reply_markup=i_btn )
    await state.set_state(AddApartment.district)

@router.message(AddApartment.district)
async def process_district(message: types.Message, state: FSMContext):
    await state.update_data(district=message.text)
    await message.answer("Manzilni to'liq kiriting:")
    await state.set_state(AddApartment.address)

@router.message(AddApartment.address)
async def process_address(message: types.Message, state: FSMContext):
    await state.update_data(address=message.text)
    await message.answer("Xonalar sonini kiriting (1-10):")
    await state.set_state(AddApartment.rooms)

@router.message(AddApartment.rooms)
async def process_rooms(message: types.Message, state: FSMContext):
    rooms = validate_rooms(message.text)
    if not rooms:
        await message.answer("❌ Noto'g'ri format. Iltimos, 1 dan 10 gacha son kiriting:")
        return
    
    await state.update_data(rooms=rooms)
    await message.answer("Kvartira qaysi qavatda joylashgan?")
    await state.set_state(AddApartment.floor)

@router.message(AddApartment.floor)
async def process_floor(message: types.Message, state: FSMContext):
    floor = validate_floor(message.text)
    if not floor:
        await message.answer("❌ Noto'g'ri format. Iltimos, qavatni raqamda kiriting:")
        return
    
    await state.update_data(floor=floor)
    await message.answer("Bino necha qavatli?")
    await state.set_state(AddApartment.total_floors)

@router.message(AddApartment.total_floors)
async def process_total_floors(message: types.Message, state: FSMContext):
    total_floors = validate_floor(message.text)
    if not total_floors:
        await message.answer("❌ Noto'g'ri format. Iltimos, qavatlar sonini raqamda kiriting:")
        return
    
    data = await state.get_data()
    if data['floor'] > total_floors:
        await message.answer("❌ Kvartira qavati binoning umumiy qavatlar sonidan katta bo'lishi mumkin emas!")
        return
    
    await state.update_data(total_floors=total_floors)
    await message.answer("Kvartira maydonini kiriting (m²):")
    await state.set_state(AddApartment.area)

@router.message(AddApartment.area)
async def process_area(message: types.Message, state: FSMContext):
    try:
        area = float(message.text.replace(',', '.'))
        if area <= 0 or area > 500:  # Maksimal maydon chegarasi
            raise ValueError
    except ValueError:
        await message.answer("❌ Noto'g'ri format. Iltimos, maydonni raqamda kiriting (m²):")
        return
    
    await state.update_data(area=area)
    await message.answer("Kvartira narxini kiriting (dollar):")
    await state.set_state(AddApartment.price)

@router.message(AddApartment.price)
async def process_price(message: types.Message, state: FSMContext):
    price = validate_price(message.text)
    if not price:
        await message.answer(
            "❌ Noto'g'ri format. Iltimos, narxni raqamda kiriting:\n"
            "Masalan: 2000000"
        )
        return
    
    await state.update_data(price=price)
    await message.answer(
        "Mebellar bormi?",
        reply_markup=furniture_keyboard
    )
    await state.set_state(AddApartment.has_furniture)

@router.message(AddApartment.has_furniture)
async def process_furniture(message: types.Message, state: FSMContext):
    if message.text not in ["✅ Ha", "❌ Yo'q"]:
        await message.answer("❌ Iltimos, tugmalardan birini tanlang:", reply_markup=furniture_keyboard)
        return
    
    has_furniture = message.text == "✅ Ha"
    await state.update_data(has_furniture=has_furniture)
    
    await message.answer(
        "Kvartira haqida qo'shimcha ma'lumot kiriting:\n"
        "(Masalan: ta'mirlangan, konditsioner bor va h.k.)"
    )
    await state.set_state(AddApartment.description)

@router.message(AddApartment.description)
async def process_description(message: types.Message, state: FSMContext):
    await state.update_data(description=message.text)
    
    await message.answer(
        "Kvartiraning rasmlarini yuboring (maksimum 10 ta).\n"
        "Yuborishni tugatgach 'Yakunlash' tugmasini bosing:",
        reply_markup=confirm_keyboard
    )
    await state.set_state(AddApartment.photos)

@router.message(AddApartment.photos, F.photo)
async def process_photo(message: types.Message, state: FSMContext):
    data = await state.get_data()
    photos = data.get('photos', [])
    
    if len(photos) >= 10:
        await message.answer("❌ Maksimum 10 ta rasm yuklash mumkin!")
        return
    
    # Rasmning file_id sini saqlash
    photos.append(message.photo[-1].file_id)
    await state.update_data(photos=photos)
    
    # Yuklangan rasmlar sonini ko'rsatish
    # await message.answer(
    #     f"✅ {len(photos)} ta rasm yuklandi.\n"
    #     "Yana rasm yuborishingiz yoki '✅ Yakunlash' tugmasini bosishingiz mumkin.",
    #     reply_markup=confirm_keyboard
    # )

@router.message(AddApartment.photos, F.text == "✅ Yakunlash")
async def finish_adding_photos(message: types.Message, state: FSMContext):
    data = await state.get_data()
    if not data.get('photos'):
        await message.answer("❌ Kamida bitta rasm yuklash kerak!")
        return
            
    try:
        # Kvartira ma'lumotlarini saqlash
        apartment = await db.add_apartment(
            owner_id=message.from_user.id,
            district=data['district'],
            address=data['address'],
            rooms=data['rooms'],
            floor=data['floor'],
            total_floors=data['total_floors'],
            price=data['price'],
            area=data['area'],
            description=data.get('description'),
            has_furniture=data['has_furniture']
        )
        
        # Rasmlarni saqlash
        for photo_id in data['photos']:
            await db.add_apartment_photo(apartment['id'], photo_id)
        
        # O'xshash kvartiralarni topish va taqqoslash
        similar_apartments = await db.get_similar_apartments(
            district=data['district'],
            rooms=data['rooms'],
            price_range=(float(data['price']) * 0.8, float(data['price']) * 1.2)  # ±20% narx oralig'i
        )
        
        # Eng yaxshi kvartira tanlash
        best_apartment = await select_best_apartment(similar_apartments)
        
        # O'xshash filterlarga ega foydalanuvchilarni topish
        similar_filters = await db.find_similar_filters(
            district=data['district'],
            min_rooms=data['rooms'],
            min_price=data['price'],
            max_price=data['price']
        )
        
        if similar_filters and best_apartment:
            media = []
            photos = await db.get_apartment_photos(best_apartment['id'])
            if photos:
                for photo in photos:
                    media.append(types.InputMediaPhoto(media=photo['photo_file_id']))
                
                for filter in similar_filters:
                    try:
                        notification_text = (
                            "🏠 Sizning filteringizga mos yangi kvartira topildi!\n\n"
                            f"Siz qidirgan parametrlar:\n"
                            f"📍 Tuman: {filter['district']}\n"
                            f"🏠 Xonalar: {filter['min_rooms']}\n"
                            f"💰 Narx oralig'i: ${filter['min_price']:,} - ${filter['max_price']:,}\n\n"
                            "Batafsil ma'lumot va bog'lanish uchun quyidagi tugmalarni bosing:"
                        )
                        
                        if media:
                            await bot.send_media_group(filter['telegram_id'], media=media)
                        
                        keyboard = InlineKeyboardBuilder()
                        keyboard.button(text="📞 Bog'lanish", callback_data=f"contact:{best_apartment['id']}")
                        keyboard.button(text="📍 Lokatsiya", callback_data=f"location:{best_apartment['id']}")
                        
                        await bot.send_message(
                            filter['telegram_id'],
                            notification_text,
                            reply_markup=keyboard.as_markup(),
                            parse_mode="HTML"
                        )
                    except Exception as e:
                        print(f"Xabar yuborishda xatolik: {e}")
        
        await message.answer(
            "✅ Kvartira muvaffaqiyatli qo'shildi!",
            reply_markup=main_landlord_keyboard
        )
        await state.clear()
        
    except Exception as e:
        print(f"Xatolik: {e}")
        await message.answer(
            "❌ Xatolik yuz berdi. Iltimos, qaytadan urinib ko'ring.",
            reply_markup=main_landlord_keyboard
        )
        await state.clear()

@router.message(F.text == "📋 Mening e'lonlarim")
async def show_my_apartments(message: types.Message):
    user = await db.get_user_by_telegram_id(message.from_user.id)
    
    if not user:
        await message.answer("❌ Siz ro'yxatdan o'tmagansiz.")
        return
        
    if user['user_type'] != 'landlord':
        await message.answer("❌ Faqat kvartira beruvchilar e'lonlarni ko'ra oladi.")
        return
    
    apartments = await db.get_user_apartments(message.from_user.id)
    
    if not apartments:
        await message.answer("❌ Sizda hozircha e'lonlar yo'q")
        return
    
    for apartment in apartments:
        photos = await db.get_apartment_photos(apartment['id'])
        media = []
        
        if photos:
            for photo in photos:
                media.append(types.InputMediaPhoto(media=photo['photo_file_id']))
            await message.answer_media_group(media=media)
        
        keyboard = InlineKeyboardBuilder()
        keyboard.button(text="🗑 O'chirish", callback_data=f"delete:{apartment['id']}")
        keyboard.button(text="❌ Yopish", callback_data="close")
        
        await message.answer(
            await format_apartment_info(apartment),
            reply_markup=keyboard.as_markup(),
            parse_mode="HTML"
        )

@router.callback_query(F.data.startswith("delete:"))
async def delete_apartment(callback: types.CallbackQuery):
    try:
        apartment_id = int(callback.data.split(":")[1])
        result = await db.delete_apartment(apartment_id)
        
        if result:
            await callback.message.delete()
            await callback.message.answer("✅ E'lon muvaffaqiyatli o'chirildi!")
        else:
            await callback.message.answer("❌ E'lon topilmadi yoki allaqachon o'chirilgan")
            
    except ValueError:
        await callback.message.answer("❌ Noto'g'ri e'lon identifikatori")
    except Exception as e:
        print(f"O'chirish xatoligi: {e}")
        await callback.message.answer("❌ Xatolik yuz berdi. Qaytadan urinib ko'ring.")
    
    await callback.answer()
