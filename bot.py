from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime
import asyncio
from config import BOT_TOKEN, ADMIN_IDS
from database import get_daily_statistics

# Инициализация бота с хранилищем состояний
bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# Класс для состояний FSM
class AddUser(StatesGroup):
    waiting_for_id = State()

def get_admin_keyboard():
    """Создает клавиатуру для администратора"""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="➕ Добавить пользователя")]
        ],
        resize_keyboard=True
    )
    return keyboard

async def load_client_ids():
    """Загружает список ID клиентов из файла"""
    try:
        with open('client_id.txt', 'r') as file:
            return [int(line.strip()) for line in file if line.strip()]
    except FileNotFoundError:
        return []

async def save_client_id(user_id: int):
    """Сохраняет ID клиента в файл"""
    with open('client_id.txt', 'a') as file:
        file.write(f"{user_id}\n")

@dp.message(Command("start"))
async def cmd_start(message: Message):
    if message.from_user.id == ADMIN_IDS:
        await message.answer(
            "Бот запущен. Вы имеете права администратора.",
            reply_markup=get_admin_keyboard()
        )
    else:
        await message.answer("Добро пожаловать! У вас нет прав администратора.")

@dp.message(F.text == "➕ Добавить пользователя")
async def add_user_start(message: Message, state: FSMContext):
    """Обработчик нажатия кнопки добавления пользователя"""
    if message.from_user.id != ADMIN_IDS:
        return
    
    await message.answer(
        "Отправьте ID пользователя (только цифры)",
        reply_markup=ReplyKeyboardRemove()
    )
    await state.set_state(AddUser.waiting_for_id)

@dp.message(AddUser.waiting_for_id)
async def add_user_finish(message: Message, state: FSMContext):
    """Обработчик получения ID пользователя"""
    if message.from_user.id != ADMIN_IDS:
        return

    try:
        user_id = int(message.text.strip())
        
        # Загружаем текущий список получателей
        current_clients = await load_client_ids()
        
        # Проверяем, не добавлен ли уже этот пользователь
        if user_id in current_clients:
            await message.answer(
                f"Пользователь с ID {user_id} уже добавлен в список получателей!",
                reply_markup=get_admin_keyboard()
            )
        else:
            # Сохраняем нового получателя
            await save_client_id(user_id)
            await message.answer(
                f"Пользователь с ID {user_id} успешно добавлен в список получателей!",
                reply_markup=get_admin_keyboard()
            )
            
            # Отправляем уведомление добавленному пользователю
            try:
                await bot.send_message(
                    user_id,
                    "Вы были добавлены в список получателей ежедневной статистики эмоций."
                )
            except Exception as e:
                await message.answer(
                    f"Пользователь добавлен, но не удалось отправить ему уведомление: {str(e)}",
                    reply_markup=get_admin_keyboard()
                )
    
    except ValueError:
        await message.answer(
            "Ошибка! ID должен состоять только из цифр.",
            reply_markup=get_admin_keyboard()
        )
    except Exception as e:
        await message.answer(
            f"Ошибка при добавлении пользователя: {str(e)}",
            reply_markup=get_admin_keyboard()
        )
    
    await state.clear()

async def send_daily_report():
    """Функция для отправки ежедневного отчета"""
    statistics = await get_daily_statistics()
    
    # Загружаем список получателей из файла
    recipient_ids = [ADMIN_IDS] + await load_client_ids()
    
    for user_id in recipient_ids:
        report_message = "📊 Ежедневный отчет по эмоциям\n\n"
        
        for institution in statistics:
            report_message += f"🏢 В учреждении {institution['name']} за {institution['date']}:\n"
            report_message += f"📌 Всего зафиксировано: {institution['total_emotions']} эмоций\n"
            report_message += f"👥 Из них в базе: {institution['registered_emotions']} эмоций\n\n"
            
            for emotion, count in institution['emotions_breakdown'].items():
                emoji = get_emotion_emoji(emotion)
                report_message += f"{emoji} {emotion}: {count}\n"
            
            report_message += "\n" + "─" * 30 + "\n\n"
        
        try:
            await bot.send_message(user_id, report_message)
        except Exception as e:
            print(f"Ошибка отправки сообщения пользователю {user_id}: {e}")

def get_emotion_emoji(emotion: str) -> str:
    """Возвращает эмодзи для каждого типа эмоции"""
    emoji_map = {
        "happy": "😊",
        "neutral": "😐",
        "angry": "😠",
        "sad": "😢"
    }
    return emoji_map.get(emotion.lower(), "❓")

async def main():
    # Настройка планировщика
    scheduler = AsyncIOScheduler(timezone="Asia/Almaty")
    
    # Настройка ежедневной отправки в определенное время (например, в 9:00)
    scheduler.add_job(send_daily_report, 'cron', hour=9, minute=0)
    
    scheduler.start()
    
    # Запуск бота
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main()) 