from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from states.user_states import ApartmentFilter
from keyboards.default.main_keyboards import main_renter_keyboard
from keyboards.inline.filter_keyboards import get_save_filter_keyboard
from loader import db
from utils.validators import validate_price, validate_rooms
from keyboards.default.main_keyboards import get_district_keyboard
router = Router()
from .apartment_listing import format_apartment_info
@router.message(F.text == "🔍 Filter o'rnatish")
async def start_filter(message: types.Message, state: FSMContext):
    tuman_inb = get_district_keyboard()
    await message.answer("Qaysi tumanda kvartira qidiryapsiz?", reply_markup=tuman_inb)
    await state.set_state(ApartmentFilter.district)

@router.message(ApartmentFilter.district)
async def process_district(message: types.Message, state: FSMContext):
    await state.update_data(district=message.text)
    await message.answer("Minimal narxni kiriting (dollar):")
    await state.set_state(ApartmentFilter.min_price)

@router.message(ApartmentFilter.min_price)
async def process_min_price(message: types.Message, state: FSMContext):
    price = validate_price(message.text)
    if not price:
        await message.answer("❌ Noto'g'ri format. Iltimos, 1000 dan 1000000000 gacha son kiriting:")
        return
    
    await state.update_data(min_price=price)
    await message.answer("Maximal narxni kiriting (dollar):")
    await state.set_state(ApartmentFilter.max_price)

@router.message(ApartmentFilter.max_price)
async def process_max_price(message: types.Message, state: FSMContext):
    price = validate_price(message.text)
    if not price:
        await message.answer("❌ Noto'g'ri format. Iltimos, 1000 dan 1000000000 gacha son kiriting:")
        return
    
    await state.update_data(max_price=price)
    await message.answer("Xonalar sonini kiriting (1 dan 10 gacha):")
    await state.set_state(ApartmentFilter.rooms)

@router.message(ApartmentFilter.rooms)
async def process_filter_rooms(message: types.Message, state: FSMContext):
    rooms = validate_rooms(message.text)
    if not rooms:
        await message.answer("❌ Noto'g'ri format. Iltimos, 1 dan 10 gacha son kiriting:")
        return
    
    data = await state.get_data()
    
    # Filter ma'lumotlarini to'plash
    filter_data = {
        'district': data['district'],
        'min_price': data['min_price'],
        'max_price': data['max_price'],
        'min_rooms': rooms
    }
    
    # Filter natijalarini ko'rsatish
    apartments = await db.get_apartments_by_filters(
        min_price=data['min_price'],
        max_price=data['max_price'],
        district=data['district'],
        min_rooms=rooms
    )
    
    if not apartments:
        # Klaviaturani yaratish
        keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
            [
                types.InlineKeyboardButton(text="💾 Filterni saqlash", callback_data="save_filter"),
                types.InlineKeyboardButton(text="❌ Yopish", callback_data="close")
            ]
        ])
        
        # Filter ma'lumotlarini state'ga saqlash
        await state.update_data(filter_data=filter_data)
        
        await message.answer(
            "❌ Afsuski, bunday parametrlar bo'yicha kvartiralar topilmadi.\n"
            "Ushbu filterni saqlab qo'yishni xohlaysizmi?",
            reply_markup=keyboard
        )
        return  # State'ni tozalamaslik uchun return
    
    await state.clear()

@router.message(F.text == "⭐️ Saqlangan filterlar")
async def show_saved_filters(message: types.Message):
    filters = await db.get_user_filters(message.from_user.id)
    
    if not filters:
        await message.answer("❌ Sizda saqlangan filterlar yo'q")
        return
    
    for filter in filters:
        text = (
            f"📍 Tuman: {filter['district']}\n"
            f"💰 Narx: {filter['min_price']:,} - {filter['max_price']:,} so'm\n"
            f"🏠 Xonalar soni: {filter['min_rooms']}"
        )
        
        keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
            [types.InlineKeyboardButton(text="🔍 Qidirish", callback_data=f"use_filter:{filter['id']}")],
            [types.InlineKeyboardButton(text="🗑 O'chirish", callback_data=f"delete_filter:{filter['id']}")]
        ])
        
        await message.answer(text, reply_markup=keyboard)

@router.callback_query(F.data == "save_filter")
async def save_filter_callback(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    filter_data = data.get('filter_data')
    
    if not filter_data:
        await callback.answer("❌ Xatolik yuz berdi")
        return
    
    try:
        # Filterni saqlash
        await db.save_filter(
            user_id=callback.from_user.id,
            district=filter_data['district'],
            min_price=filter_data['min_price'],
            max_price=filter_data['max_price'],
            min_rooms=filter_data['min_rooms']
        )
        
        # Muvaffaqiyatli saqlangani haqida xabar
        await callback.message.edit_text(
            "✅ Filter muvaffaqiyatli saqlandi!\n"
            "Saqlangan filterlarni ko'rish uchun '⭐️ Saqlangan filterlar' tugmasini bosing."
        )
        
    except Exception as e:
        print(f"Filter saqlashda xatolik: {e}")
        await callback.message.edit_text("❌ Xatolik yuz berdi. Qaytadan urinib ko'ring.")
    
    await state.clear()
    await callback.answer()

@router.callback_query(F.data == "close")
async def close_filter(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.delete()
    await state.clear()
    await callback.answer()

@router.callback_query(F.data.startswith("delete_filter:"))
async def delete_filter_callback(callback: types.CallbackQuery):
    filter_id = int(callback.data.split(":")[1])
    
    try:
        await db.delete_filter(filter_id)
        await callback.message.edit_text("✅ Filter o'chirildi!")
    except Exception as e:
        await callback.message.answer("❌ Xatolik yuz berdi. Qaytadan urinib ko'ring.")
    
    await callback.answer()

@router.callback_query(F.data.startswith("use_filter:"))
async def use_saved_filter(callback: types.CallbackQuery):
    filter_id = int(callback.data.split(":")[1])
    
    try:
        # Saqlangan filterni olish
        saved_filter = await db.get_filter_by_id(filter_id)
        if not saved_filter:
            await callback.answer("❌ Filter topilmadi")
            return
        
        # Filter bo'yicha kvartiralarni qidirish
        apartments = await db.get_apartments_by_filters(
            min_price=saved_filter['min_price'],
            max_price=saved_filter['max_price'],
            district=saved_filter['district'],
            min_rooms=saved_filter['min_rooms']
        )
        
        if not apartments:
            await callback.message.answer(
                "❌ Afsuski, bunday parametrlar bo'yicha kvartiralar topilmadi.",
                reply_markup=main_renter_keyboard
            )
        else:
            await callback.message.answer(
                f"✅ {len(apartments)} ta kvartira topildi:",
                reply_markup=main_renter_keyboard
            )
            
            for apartment in apartments:
                photos = await db.get_apartment_photos(apartment['id'])
                media = []
                
                if photos:
                    for photo in photos:
                        media.append(types.InputMediaPhoto(media=photo['photo_file_id']))
                    await callback.message.answer_media_group(media=media)
                
                await callback.message.answer(
                    await format_apartment_info(apartment),
                    reply_markup=create_apartment_keyboard(apartment['id']),
                    parse_mode="HTML"
                )
    
    except Exception as e:
        print(f"Saqlangan filter ishlatishda xatolik: {e}")
        await callback.message.answer("❌ Xatolik yuz berdi. Qaytadan urinib ko'ring.")
    
    await callback.answer()