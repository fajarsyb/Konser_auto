import os
import requests
import logging

logging.basicConfig(level=logging.INFO)

def send_telegram_alert(message):
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")

    if not token or not chat_id:
        logging.warning("Telegram token atau chat ID belum diset di .env")
        return

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "HTML"
    }

    try:
        response = requests.post(url, json=payload)
        if response.status_code != 200:
            logging.error(f"Gagal kirim Telegram: {response.text}")
        else:
            logging.info("Notifikasi Telegram berhasil dikirim.")
    except Exception as e:
        logging.error(f"Error saat mengirim Telegram: {e}")
