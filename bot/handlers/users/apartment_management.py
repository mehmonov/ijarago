from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from aiogram.exceptions import TelegramBadRequest

from utils.validators import validate_price, validate_rooms, validate_floor
from states.user_states import AddApartment
from keyboards.default.main_keyboards import (
    confirm_keyboard,
    furniture_keyboard,
    main_landlord_keyboard
)

router = Router()

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

@router.message(AddApartment.photos)
async def process_photos(message: types.Message, state: FSMContext):
    if not message.photo:
        await message.answer("❌ Iltimos, rasm yuboring yoki 'Yakunlash' tugmasini bosing")
        return
    
    data = await state.get_data()
    photos = data.get('photos', [])
    
    if len(photos) >= 10:
        await message.answer("❌ Maksimal 10 ta rasm yuklash mumkin")
        return
    
    photos.append(message.photo[-1].file_id)
    await state.update_data(photos=photos)
    
    await message.answer(
        f"✅ {len(photos)}-rasm qabul qilindi. Yana rasm yuborishingiz yoki 'Yakunlash' tugmasini bosishingiz mumkin",
        reply_markup=confirm_keyboard
    )

@router.message(F.text == "Yakunlash", AddApartment.photos)
async def finish_adding_apartment(message: types.Message, state: FSMContext):
    data = await state.get_data()
    
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
        if 'photos' in data:
            for photo_id in data['photos']:
                await db.add_apartment_photo(apartment['id'], photo_id)
        
        await message.answer(
            "✅ Kvartira muvaffaqiyatli qo'shildi!",
            reply_markup=main_landlord_keyboard
        )
        await state.clear()
        
    except Exception as e:
        await message.answer(
            "❌ Xatolik yuz berdi. Iltimos, qaytadan urinib ko'ring.",
            reply_markup=main_landlord_keyboard
        )
        await state.clear()