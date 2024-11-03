from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardMarkup

from utils.validators import validate_price
from states.user_states import ApartmentFilter
from loader import db

router = Router()

def create_apartment_keyboard(apartment_id: int):
    builder = InlineKeyboardBuilder()
    builder.button(text="📞 Bog'lanish", callback_data=f"contact:{apartment_id}")
    builder.button(text="📍 Lokatsiya", callback_data=f"location:{apartment_id}")
    builder.button(text="❌ Yopish", callback_data="close")
    
    return builder.as_markup()

async def format_apartment_info(apartment: dict):
    text = f"🏠 <b>{apartment['rooms']} xonali kvartira</b>\n"
    text += f"📍 <b>Manzil:</b> {apartment['district']}, {apartment['address']}\n"
    text += f"💰 <b>Narxi:</b> {apartment['price']:,} so'm\n"
    text += f"📏 <b>Maydoni:</b> {apartment['area']} m²\n"
    text += f"🏢 <b>Qavat:</b> {apartment['floor']}/{apartment['total_floors']}\n"
    text += f"🪑 <b>Mebel:</b> {'Bor' if apartment['has_furniture'] else 'Yoq'}\n"
    text += f"👤 <b>Egasi:</b> {apartment['owner_name']}\n\n"
    text += f"📝 <b>Tavsif:</b>\n{apartment['description']}"
    
    return text

@router.message(F.text == "🏠 Kvartiralarni ko'rish")
async def show_apartments(message: types.Message):
    apartments = await db.get_all_available_apartments()
    
    if not apartments:
        await message.answer("❌ Hozircha e'lonlar yo'q")
        return
    
    for apartment in apartments:
        photos = await db.get_apartment_photos(apartment['id'])
        media = []
        
        if photos:
            for photo in photos:
                media.append(types.InputMediaPhoto(media=photo['photo_file_id']))
            
            await message.answer_media_group(media=media)
        
        await message.answer(
            await format_apartment_info(apartment),
            reply_markup=create_apartment_keyboard(apartment['id']),
            parse_mode="HTML"
        )

@router.message(F.text == "🔍 Filter o'rnatish")
async def start_filter(message: types.Message, state: FSMContext):
    await message.answer(
        "Qaysi tumanda kvartira qidiryapsiz?\n"
        "Masalan: Chilonzor, Yunusobod, ..."
    )
    await state.set_state(ApartmentFilter.district)

@router.message(ApartmentFilter.district)
async def process_filter_district(message: types.Message, state: FSMContext):
    await state.update_data(district=message.text)
    await message.answer(
        "Minimal narxni kiriting (so'm):\n"
        "Masalan: 2000000"
    )
    await state.set_state(ApartmentFilter.min_price)

@router.message(ApartmentFilter.min_price)
async def process_filter_min_price(message: types.Message, state: FSMContext):
    price = validate_price(message.text)
    if not price:
        await message.answer("❌ Noto'g'ri format. Iltimos, narxni raqamda kiriting:")
        return
    
    await state.update_data(min_price=price)
    await message.answer(
        "Maksimal narxni kiriting (so'm):\n"
        "Masalan: 5000000"
    )
    await state.set_state(ApartmentFilter.max_price)

@router.message(ApartmentFilter.max_price)
async def process_filter_max_price(message: types.Message, state: FSMContext):
    price = validate_price(message.text)
    if not price:
        await message.answer("❌ Noto'g'ri format. Iltimos, narxni raqamda kiriting:")
        return
    
    data = await state.get_data()
    if price <= data['min_price']:
        await message.answer("❌ Maksimal narx minimal narxdan katta bo'lishi kerak:")
        return
    
    await state.update_data(max_price=price)
    await message.answer("Xonalar sonini kiriting (1-10):")
    await state.set_state(ApartmentFilter.rooms)

@router.message(ApartmentFilter.rooms)
async def process_filter_rooms(message: types.Message, state: FSMContext):
    rooms = validate_rooms(message.text)
    if not rooms:
        await message.answer("❌ Noto'g'ri format. Iltimos, 1 dan 10 gacha son kiriting:")
        return
    
    data = await state.get_data()
    
    # Filter natijalarini ko'rsatish
    apartments = await db.get_apartments_by_filters(
        min_price=data['min_price'],
        max_price=data['max_price'],
        district=data['district'],
        min_rooms=rooms
    )
    
    if not apartments:
        await message.answer(
            "❌ Afsuski, bunday parametrlar bo'yicha kvartiralar topilmadi.",
            reply_markup=main_renter_keyboard
        )
    else:
        await message.answer(
            f"✅ {len(apartments)} ta kvartira topildi:",
            reply_markup=main_renter_keyboard
        )
        
        for apartment in apartments:
            photos = await db.get_apartment_photos(apartment['id'])
            media = []
            
            if photos:
                for photo in photos:
                    media.append(types.InputMediaPhoto(media=photo['photo_file_id']))
                
                await message.answer_media_group(media=media)
            
            await message.answer(
                await format_apartment_info(apartment),
                reply_markup=create_apartment_keyboard(apartment['id']),
                parse_mode="HTML"
            )
    
    await state.clear()

@router.callback_query(F.data.startswith("contact:"))
async def show_contact(callback: types.CallbackQuery):
    apartment_id = int(callback.data.split(":")[1])
    apartment = await db.get_apartment_by_id(apartment_id)
    
    if not apartment:
        await callback.answer("❌ E'lon topilmadi")
        return
    
    owner = await db.get_user_by_telegram_id(apartment['owner_id'])
    await callback.message.answer(
        f"📞 Telefon: {owner['phone']}\n"
        f"👤 Egasi: {owner['full_name']}"
    )
    await callback.answer()