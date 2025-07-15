from aiogram import Bot
from aiogram.enums.parse_mode import ParseMode
from utils.db.postgres import Database
from utils.db.models.users import UserQueries
from utils.db.models.apartments import ApartmentQueries
from utils.db.models.photos import PhotoQueries
from utils.db.models.filters import FilterQueries
from data.config import BOT_TOKEN

db = Database()
bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML)
