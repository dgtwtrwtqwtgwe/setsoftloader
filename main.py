from aiogram import Bot, Dispatcher, types
from aiogram.types import WebAppInfo
from aiogram.filters import Command
from aiohttp import web
import asyncio
import logging
import requests
import json
import os

# Настройки
API_TOKEN = "8460820194:AAHaqb2bsLGaH1BMGuuK80F7l2YI0TTExDc"  # Токен бота от @BotFather
ATLAS_TOKEN = "5486553522:1PL3JMD1AB"  # Ваш токен Atlas
ATLAS_URL = "https://api.atlass.digital"
load_dotenv()
tokened = os.getenv('BOT_TOKEN')
# Инициализация бота
bot = Bot(token=tokened)
dp = Dispatcher()

# Хранилище для данных (в продакшене используйте БД)
requests_data = {}

async def handle_atlas_request(data):
    """Обработка запросов к Atlas API"""
    try:
        headers = {"Content-Type": "application/json"}
        payload = {
            "token": ATLAS_TOKEN,
            "type": data["type"],
            "search": data["search"],
            "method": data.get("method", "lite")
        }
        
        response = requests.post(ATLAS_URL, json=payload, headers=headers)
        return response.json()
    except Exception as e:
        return {"error": str(e)}

# HTTP API endpoints
async def handle_search(request):
    """Обработчик поисковых запросов"""
    try:
        data = await request.json()
        required_fields = ['type', 'search']
        
        if not all(field in data for field in required_fields):
            return web.json_response({"error": "Missing required fields"}, status=400)
        
        # Валидация типа поиска
        valid_types = ['email', 'ip', 'phone', 'fio']
        if data['type'] not in valid_types:
            return web.json_response({"error": "Invalid search type"}, status=400)
        
        # Отправляем запрос в Atlas
        result = await handle_atlas_request(data)
        return web.json_response(result)
        
    except Exception as e:
        return web.json_response({"error": f"Internal server error: {str(e)}"}, status=500)

async def health_check(request):
    """Проверка работоспособности API"""
    return web.json_response({"status": "ok", "service": "Atlas API Bot"})

# Команды бота
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(
        "🤖 Atlas API Bot\n\n"
        "Этот бот предоставляет безопасный доступ к Atlas API.\n"
        "Используйте HTTP запросы к нашему API endpoint."
    )

def setup_routes(app):
    """Настройка маршрутов API"""
    app.router.add_post('/api/search', handle_search)
    app.router.add_get('/health', health_check)

async def start_bot():
    """Запуск бота и веб-сервера"""
    # Запускаем поллинг бота в фоне
    bot_task = asyncio.create_task(dp.start_polling(bot))
    
    # Создаем и запускаем веб-сервер
    app = web.Application()
    setup_routes(app)
    
    runner = web.AppRunner(app)
    await runner.setup()
    
    site = web.TCPSite(runner, '0.0.0.0', 8080)
    await site.start()
    
    print("🚀 API Bot запущен!")
    print("📡 HTTP сервер слушает на порту 8080")
    print("🔗 Endpoint: POST http://your-host:8080/api/search")
    
    # Ожидаем завершения обеих задач
    await bot_task

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(start_bot())
