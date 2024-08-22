import asyncio
import logging
from aiogram import Bot, Dispatcher
from config import API_TOKEN
from handlers import router

# Включаем логирование
logging.basicConfig(level=logging.INFO)

# Создаем объект бота с токеном
bot = Bot(token=API_TOKEN)
# Создаем диспетчер для обработки сообщений и событий
dp = Dispatcher()
# Подключаем роутер с обработчиками
dp.include_router(router)

async def main():
    # Запускаем бота
    # Запускаем бота
    await dp.start_polling(bot)

if __name__ == '__main__':
    # Запускаем главное событие
    asyncio.run(main())   