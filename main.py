from flask import Flask, request, jsonify
import requests
import os
from dotenv import load_dotenv
import telebot

load_dotenv()
app = Flask(__name__)

BOT_TOKEN = os.getenv('BOT_TOKEN')
ATLAS_TOKEN = "5486553522:1PL3JMD1AB"

bot = telebot.TeleBot(BOT_TOKEN)
ATLAS_URL = "https://api.atlass.digital"

def handle_atlas_request(data):
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

@app.route('/api/search', methods=['POST'])
def handle_search():
    try:
        data = request.get_json()
        required_fields = ['type', 'search']
        
        if not all(field in data for field in required_fields):
            return jsonify({"error": "Missing required fields"}), 400
        
        valid_types = ['email', 'ip', 'phone', 'fio']
        if data['type'] not in valid_types:
            return jsonify({"error": "Invalid search type"}), 400
        
        result = handle_atlas_request(data)
        return jsonify(result)
        
    except Exception as e:
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "ok", "service": "Atlas API Bot"})

@bot.message_handler(commands=['start'])
def cmd_start(message):
    bot.send_message(message.chat.id, "🤖 Atlas API Bot\n\nЭтот бот предоставляет безопасный доступ к Atlas API.")

def run_bot():
    bot.polling(none_stop=True)

if __name__ == "__main__":
    from threading import Thread
    bot_thread = Thread(target=run_bot)
    bot_thread.start()
    app.run(host='0.0.0.0', port=8080)
