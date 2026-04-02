import os
import asyncio
import random
import logging
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder

# ==========================================
# ЧАСТЬ 1: ОБМАНКА ДЛЯ RENDER (Health Check)
# ==========================================
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK")

def run_health_check():
    # Render сам назначит порт через переменную окружения PORT
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(('0.0.0.0', port), HealthCheckHandler)
    logging.info(f"Health check server started on port {port}")
    server.serve_forever()

# Запускаем сервер в отдельном потоке, чтобы он не мешал боту
threading.Thread(target=run_health_check, daemon=True).start()

# ==========================================
# ЧАСТЬ 2: ОСНОВНОЙ КОД БОТА
# ==========================================
API_TOKEN = '8797100348:AAGsvV-XF2IWwuv0VtOW919dgNwhsdXr-bw'
ADMIN_ID = 7594795969

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# База сплетен (пока просто список)
gossips = ["В школе 221 сегодня отличный день! ✨"]

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("Приветик! Ты попал в СПЛЕТНИЦУ 221 школы. Послушай или скинь сплетню в бота) 🤫")

@dp.message(F.text)
async def handle_message(message: types.Message):
    if message.text == "/start":
        return
    
    # Создаем кнопки Одобрить/Отклонить для админа
    builder = InlineKeyboardBuilder()
    builder.button(text="✅ Одобрить", callback_data="accept")
    builder.button(text="❌ Удалить", callback_data="decline")

    # Пересылаем сообщение админу
    await bot.send_message(
        ADMIN_ID,
        f"📩 Новая сплетня от @{message.from_user.username or 'скрыто'}:\n\n{message.text}",
        reply_markup=builder.as_markup()
    )
    await message.answer("✅ Твоя сплетня отправлена на проверку админу!")

@dp.callback_query(F.data == "accept")
async def accept_gossip(callback: types.CallbackQuery):
    try:
        # Берем текст сплетни из сообщения админа
        new_gossip = callback.message.text.split('\n\n')[1]
        gossips.append(new_gossip)
        await callback.message.edit_text(f"✅ **ОДОБРЕНО:**\n{new_gossip}")
    except:
        await callback.message.edit_text("Ошибка при одобрении.")
    await callback.answer()

@dp.callback_query(F.data == "decline")
async def decline_gossip(callback: types.CallbackQuery):
    await callback.message.edit_text("❌ **УДАЛЕНО**")
    await callback.answer()

async def main():
    logging.info("Бот запущен и готов к работе!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
