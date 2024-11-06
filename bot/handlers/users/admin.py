import logging
import asyncio
from aiogram import Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from loader import db, bot
from keyboards.inline.buttons import are_you_sure_markup
from states.test import AdminState
from filters.admin import IsBotAdminFilter
from data.config import ADMINS
from utils.pgtoexcel import export_to_excel
import os

router = Router()


@router.message(Command('allusers'), IsBotAdminFilter(ADMINS))
async def get_all_users(message: types.Message):
    users = await db.get_all_users()

    file_path = f"data/users_list.xlsx"
    await export_to_excel(data=users, headings=['ID', 'Full Name', 'Username', 'Telegram ID'], filepath=file_path)

    await message.answer_document(types.input_file.FSInputFile(file_path))
    os.remove(file_path)


@router.message(Command('reklama'), IsBotAdminFilter(ADMINS))
async def ask_ad_content(message: types.Message, state: FSMContext):
    await message.answer("Reklama uchun post yuboring")
    await state.set_state(AdminState.ask_ad_content)


@router.message(AdminState.ask_ad_content, IsBotAdminFilter(ADMINS))
async def send_ad_to_users(message: types.Message, state: FSMContext):
    users = await db.get_all_users()
    count = 0
    failed = 0
    
    for user in users:
        user_id = user['telegram_id']
        try:
            await message.send_copy(chat_id=user_id)
            count += 1
            await asyncio.sleep(0.05)
        except Exception as error:
            failed += 1
            logging.error(f"Ad did not send to user: {user_id}. Error: {error}")
    
    await message.answer(
        f"Reklama yuborish yakunlandi:\n"
        f"✅ Muvaffaqiyatli: {count} ta\n"
        f"❌ Muvaffaqiyatsiz: {failed} ta"
    )
    await state.clear()


@router.message(Command('cleandb'), IsBotAdminFilter(ADMINS))
async def ask_are_you_sure(message: types.Message, state: FSMContext):
    msg = await message.reply("Haqiqatdan ham bazani tozalab yubormoqchimisiz?", reply_markup=are_you_sure_markup)
    await state.update_data(msg_id=msg.message_id)
    await state.set_state(AdminState.are_you_sure)


@router.callback_query(AdminState.are_you_sure, IsBotAdminFilter(ADMINS))
async def clean_db(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    msg_id = data.get('msg_id')
    if call.data == 'yes':
        await db.delete_users()
        text = "Baza tozalandi!"
    elif call.data == 'no':
        text = "Bekor qilindi."
    await bot.edit_message_text(text=text, chat_id=call.message.chat.id, message_id=msg_id)
    await state.clear()


@router.message(Command('stats'), IsBotAdminFilter(ADMINS))
async def get_users_statistics(message: types.Message):
    total_users = await db.get_users_count()
    renters = await db.get_renters_count()
    landlords = await db.get_landlords_count()
    starts = await db.get_starts_count()
    new_users = await db.get_users_count_last_week()
    apartments = await db.get_apartments_count()

    await message.answer(
        f"📊 Bot statistikasi:\n\n"
        f"👥 Jami foydalanuvchilar: {total_users}\n"
        f"👥 Botga kirganlar soni: {starts}\n"
        f"👥 Oxirgi 7 kundagi yangi a'zolar: {new_users}\n"
        f"👤 Ijarachi (Renter)lar: {renters}\n"
        f"🏠 Ijaraga beruvchi (Landlord)lar: {landlords}\n"
        f"🏢 Jami e'lonlar soni: {apartments}"
    )
