import asyncio
import random
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder

# --- НАСТРОЙКИ ---
API_TOKEN = '8797100348:AAGsvV-XF2IWwuv0VtOW9l9dgNwhsdXr-bw'
ADMIN_ID = 7594795969 
# -----------------

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

gossips = ["В школе 221 сегодня отличный день! ✨"]

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("приветик! ты попал в СПЛЕТНИЦУ 221 школы, послушай или скинь сплетню в бота) 🤫")

@dp.message(Command("help"))
async def cmd_help(message: types.Message):
    help_text = (
        "❓ **Доступные команды:**\n\n"
        "/gossip - послушать случайную сплетню\n"
        "/sendgossip - как отправить свою новость\n"
        "/earnings - узнать про заработок\n"
        "/help - показать это сообщение"
    )
    await message.answer(help_text, parse_mode="Markdown")

@dp.message(Command("sendgossip"))
async def cmd_send_info(message: types.Message):
    await message.answer("Чтобы отправить сплетню, просто напиши её мне обычным сообщением. Я отправлю её админу на проверку, и если она ок — её увидят все! 📩")

@dp.message(Command("gossip"))
async def get_gossip(message: types.Message):
    if gossips:
        await message.answer(f"🤫 Сплетня: {random.choice(gossips)}")
    else:
        await message.answer("Сплетен пока нет, будь первым!")

@dp.message(Command("earnings"))
async def cmd_earnings(message: types.Message):
    await message.answer("💰 По вопросам заработка пиши админу: @Iilslat")

# ОБРАБОТКА ТЕКСТА (Модерация)
@dp.message(F.text)
async def handle_text(message: types.Message):
    # Если сообщение начинается с /, значит это неизвестная команда, игнорируем
    if message.text.startswith('/'):
        return
    
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(text="✅ Одобрить", callback_data="accept"))
    builder.add(types.InlineKeyboardButton(text="❌ Удалить", callback_data="decline"))

    await bot.send_message(
        ADMIN_ID, 
        f"📩 Новая сплетня от @{message.from_user.username}:\n\n{message.text}",
        reply_markup=builder.as_markup()
    )
    await message.answer("✅ Твоя сплетня отправлена на проверку админу!")

@dp.callback_query(F.data == "accept")
async def accept_gossip(callback: types.CallbackQuery):
    try:
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
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())