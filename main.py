from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

import asyncio
import warnings

from config import BOT_TOKEN
from services.news import background_news_loop
from services.cache import get_cache

# убираем предупреждения
warnings.filterwarnings("ignore")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)


# 🔘 меню
menu = ReplyKeyboardMarkup(resize_keyboard=True)
menu.add(KeyboardButton("📰 News"))


# 🚀 старт
@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    await message.reply(
        "📊 Stock News Bot\n\n"
        "Нажми 📰 News чтобы получить новости за последний час",
        reply_markup=menu
    )


# 📰 получение новостей
@dp.message_handler(lambda msg: msg.text == "📰 News")
async def send_news(message: types.Message):

    news = get_cache()

    if not news:
        await message.reply("⚠️ Пока нет данных, подожди обновления...")
        return

    # 🔥 ограничение (чтобы не спамить)
    news = news[:20]

    for n in news:

        keyboard = InlineKeyboardMarkup().add(
            InlineKeyboardButton("🔗 Открыть", url=n["url"])
        )

        text = (
            f"🟦 <b>{n['company']}</b>\n"
            f"{n['title']}\n"
            f"🕒 {n['time']}"
        )

        await message.answer(
            text,
            reply_markup=keyboard,
            parse_mode="HTML"
        )


# 🔄 background обновление
async def on_startup(dp):
    asyncio.create_task(background_news_loop())


if __name__ == "__main__":
    executor.start_polling(
        dp,
        skip_updates=True,
        on_startup=on_startup
    )