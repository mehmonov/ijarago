from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from states.user_states import ApartmentFilter

router = Router()

@router.message(F.text == "🔍 Filter o'rnatish")
async def start_filter(message: types.Message, state: FSMContext):
    await message.answer("Qaysi tumanda kvartira qidiryapsiz?")
    await state.set_state(ApartmentFilter.district)

@router.message(ApartmentFilter.district)
async def process_district(message: types.Message, state: FSMContext):
    await state.update_data(district=message.text)
    await message.answer("Minimal narxni kiriting (so'm):")
    await state.set_state(ApartmentFilter.min_price)

# Qolgan filter handlerlar...