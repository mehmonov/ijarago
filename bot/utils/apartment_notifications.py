from loader import db, bot
from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, InputMediaPhoto
from aiogram.utils.keyboard import InlineKeyboardBuilder

async def send_apartment_match_notifications(new_apartment):
    all_filters = await db.get_all_filters()
    
    for filter_item in all_filters:
        # Check if the new apartment matches the filter criteria
        if (
            new_apartment['district'] == filter_item['district'] and
            new_apartment['rooms'] >= filter_item['min_rooms'] and
            new_apartment['price'] >= filter_item['min_price'] and
            new_apartment['price'] <= filter_item['max_price'] and
            new_apartment['id'] > filter_item['last_notified_apartment_id']
        ):
            # Send notification
            try:
                notification_text = (
                    "🏠 Sizning filteringizga mos yangi kvartira topildi!\n\n"
                    f"Siz qidirgan parametrlar:\n"
                    f"📍 Tuman: {filter_item['district']}\n"
                    f"🏠 Xonalar: {filter_item['min_rooms']}\n"
                    f"💰 Narx oralig'i: ${filter_item['min_price']:,} - ${filter_item['max_price']:,}\n\n"
                    "Batafsil ma'lumot va bog'lanish uchun quyidagi tugmalarni bosing:"
                )
                
                # Fetch photos for the new apartment
                photos = await db.get_photos_by_apartment_id(new_apartment['id'])
                media = []
                if photos:
                    for photo in photos:
                        media.append(types.InputMediaPhoto(media=photo['file_id']))
                    await bot.send_media_group(filter_item['user_id'], media=media)
                
                keyboard = InlineKeyboardBuilder()
                keyboard.button(text="📞 Bog'lanish", callback_data=f"contact:{new_apartment['id']}")
                keyboard.button(text="📍 Lokatsiya", callback_data=f"location:{new_apartment['id']}")
                
                await bot.send_message(
                    filter_item['user_id'],
                    notification_text,
                    reply_markup=keyboard.as_markup(),
                    parse_mode="HTML"
                )
                
                # Update last_notified_apartment_id for this filter
                await db.update_last_notified_apartment_id(filter_item['id'], new_apartment['id'])

            except Exception as e:
                print(f"Error sending notification to user {filter_item['user_id']}: {e}")
