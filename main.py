import logging
import asyncio
from aiogram import Bot, Dispatcher, executor, types
from config import BOT_TOKEN
from services.news import get_all_news

# логирование
logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)


# ===== КНОПКА =====
@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add("📰 News")

    await message.answer("Выбери:", reply_markup=keyboard)


# ===== НОВОСТИ =====
@dp.message_handler(lambda message: message.text == "📰 News")
async def send_news(message: types.Message):
    await message.answer("⏳ Загружаю новости...")

    news = get_all_news()

    if not news:
        await message.answer("❌ Нет новостей за последний час")
        return

    for item in news:
        text = (
            f"<b>{item['company']}</b>\n\n"
            f"<b>Заголовок:</b> {item['title']}\n"
            f"<b>Источник:</b> {item['source']}\n"
            f"<b>Время:</b> {item['time']}\n\n"
            f"<a href='{item['link']}'>Читать</a>"
        )

        await message.answer(text, parse_mode="HTML", disable_web_page_preview=True)


# ===== BACKGROUND UPDATE (каждые 30 минут) =====
async def background_updates():
    while True:
        print("🔄 Обновление новостей...")
        get_all_news()
        await asyncio.sleep(1800)  # 30 минут


async def on_startup(dp):
    asyncio.create_task(background_updates())


# ===== FAKE SERVER ДЛЯ RENDER =====
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is running")

def run_web():
    server = HTTPServer(("0.0.0.0", 10000), Handler)
    server.serve_forever()

threading.Thread(target=run_web).start()


# ===== ЗАПУСК =====
if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)