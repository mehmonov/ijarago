from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardMarkup
from aiogram.fsm.state import State, StatesGroup

from utils.validators import validate_price, validate_rooms
from states.user_states import ApartmentFilter
from loader import db
from keyboards.default.main_keyboards import main_renter_keyboard, get_district_keyboard

router = Router()

# Yangi state qo'shamiz
class ApartmentListing(StatesGroup):
    select_district = State()
    viewing = State()

ITEMS_PER_PAGE = 5  # Har bir sahifada ko'rsatiladigan kvartiralar soni

def create_apartment_keyboard(apartment_id: int):
    builder = InlineKeyboardBuilder()
    builder.button(text="📞 Bog'lanish", callback_data=f"contact:{apartment_id}")
    builder.button(text="📍 Lokatsiya", callback_data=f"location:{apartment_id}")
    builder.button(text="❌ Yopish", callback_data="close")
    
    return builder.as_markup()

async def format_apartment_info(apartment: dict):
    text = f"🏠 <b>{apartment['rooms']} xonali kvartira</b>\n"
    text += f"📍 <b>Manzil:</b> {apartment['district']}, {apartment['address']}\n"
    text += f"💰 <b>Narxi:</b> ${apartment['price']:,}\n"
    text += f"📏 <b>Maydoni:</b> {apartment['area']} m²\n"
    text += f"🏢 <b>Qavat:</b> {apartment['floor']}/{apartment['total_floors']}\n"
    text += f"🪑 <b>Mebel:</b> {'Bor' if apartment['has_furniture'] else 'Yoq'}\n"
    
    # owner_name yoki owner_username borligini tekshirish
    if 'owner_name' in apartment:
        text += f"👤 <b>Egasi:</b> {apartment['owner_name']}\n"
    elif 'owner_username' in apartment:
        text += f"👤 <b>Egasi:</b> {apartment['owner_username']}\n"
    
    text += f"\n📝 <b>Tavsif:</b>\n{apartment.get('description', '')}"
    
    return text

@router.message(F.text == "🏠 Kvartiralarni ko'rish")
async def start_viewing_apartments(message: types.Message, state: FSMContext):
    i_btn = get_district_keyboard()
    await message.answer("Qaysi tumandagi kvartiralarni ko'rmoqchisiz?", reply_markup=i_btn)
    await state.set_state(ApartmentListing.select_district)

@router.message(ApartmentListing.select_district)
async def show_district_apartments(message: types.Message, state: FSMContext):
    district = message.text
    
    # Tanlangan tumandagi kvartiralarni olish
    apartments = await db.get_apartments_by_district(district)
    
    if not apartments:
        await message.answer(
            f"❌ {district} tumanida hozircha e'lonlar yo'q",
            reply_markup=main_renter_keyboard
        )
        await state.clear()
        return
    
    # Kvartiralar va sahifa ma'lumotlarini state'ga saqlash
    await state.update_data(
        district=district,
        apartments=apartments,
        current_page=1,
        total_pages=(len(apartments) + ITEMS_PER_PAGE - 1) // ITEMS_PER_PAGE
    )
    
    await show_page(message, state)
    await state.set_state(ApartmentListing.viewing)

async def show_page(message: types.Message, state: FSMContext, edit_message: bool = False):
    data = await state.get_data()
    current_page = data['current_page']
    total_pages = data['total_pages']
    apartments = data['apartments']
    
    # Joriy sahifa uchun kvartiralar
    start_idx = (current_page - 1) * ITEMS_PER_PAGE
    end_idx = start_idx + ITEMS_PER_PAGE
    page_apartments = apartments[start_idx:end_idx]
    
    # Sahifa haqida ma'lumot
    info_text = (
        f"📋 {data['district']} tumani, {current_page}-sahifa
"
        f"Jami: {len(apartments)} ta e'lon"
    )
    
    if edit_message:
        await message.edit_text(info_text, reply_markup=main_renter_keyboard)
    else:
        await message.answer(info_text, reply_markup=main_renter_keyboard)
    
    for apartment in page_apartments:
        photos = await db.get_apartment_photos(apartment['id'])
        media = []
        
        if photos:
            for photo in photos:
                media.append(types.InputMediaPhoto(media=photo['photo_file_id']))
            await message.answer_media_group(media=media)
        
        # Asosiy tugmalar va paginatsiya
        keyboard = InlineKeyboardBuilder()
        
        # Asosiy tugmalar
        keyboard.row(
            types.InlineKeyboardButton(text="📞 Bog'lanish", callback_data=f"contact:{apartment['id']}"),
            types.InlineKeyboardButton(text="📍 Lokatsiya", callback_data=f"location:{apartment['id']}")
        )
        
        # Paginatsiya tugmalari
        if total_pages > 1:
            nav_buttons = []
            if current_page > 1:
                nav_buttons.append(types.InlineKeyboardButton(text="⬅️ Oldingi", callback_data="prev_page"))
            nav_buttons.append(types.InlineKeyboardButton(text=f"{current_page}/{total_pages}", callback_data="current_page"))
            if current_page < total_pages:
                nav_buttons.append(types.InlineKeyboardButton(text="Keyingi ➡️", callback_data="next_page"))
            keyboard.row(*nav_buttons)
        
        # Yopish tugmasi
        keyboard.row(types.InlineKeyboardButton(text="❌ Yopish", callback_data="close"))
        
        await message.answer(
            await format_apartment_info(apartment),
            reply_markup=keyboard.as_markup(),
            parse_mode="HTML"
        )

@router.callback_query(F.data == "prev_page")
async def prev_page(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    if data['current_page'] > 1:
        await state.update_data(current_page=data['current_page'] - 1)
        await show_page(callback.message, state, edit_message=True)
    await callback.answer()

@router.callback_query(F.data == "next_page")
async def next_page(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    if data['current_page'] < data['total_pages']:
        await state.update_data(current_page=data['current_page'] + 1)
        await show_page(callback.message, state, edit_message=True)
    await callback.answer()

@router.callback_query(F.data == "close")
async def close_apartment(callback: types.CallbackQuery):
    await callback.message.delete()
    await callback.answer()

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