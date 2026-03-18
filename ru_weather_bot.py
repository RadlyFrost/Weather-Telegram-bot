
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = "8705550020:AAEj9G6ZulWCh7qx3kbOnOw9LNLh9pZK6iA"


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Напишите название города 🌍")


async def weather(update: Update, context: ContextTypes.DEFAULT_TYPE):
    city = update.message.text.strip()

    try:
        # 1️⃣ Получаем координаты города через Nominatim
        geo_url = f"https://nominatim.openstreetmap.org/search?q={city}&format=json&limit=1"

        geo_response = requests.get(
            geo_url,
            headers={"User-Agent": "weather-bot"},
            timeout=5
        )

        geo_data = geo_response.json()

        if not geo_data:
            await update.message.reply_text("❌ Город не найден")
            return

        lat = geo_data[0]["lat"]
        lon = geo_data[0]["lon"]

        # 2️⃣ Получаем погоду через Open-Meteo
        weather_url = (
            f"https://api.open-meteo.com/v1/forecast?"
            f"latitude={lat}&longitude={lon}"
            f"&current_weather=true"
            f"&hourly=relativehumidity_2m,cloudcover"
        )

        weather_response = requests.get(weather_url, timeout=5)
        weather_data = weather_response.json()

        current = weather_data.get("current_weather")

        if not current:
            await update.message.reply_text("❌ Не удалось получить погоду")
            return

        # данные
        temp = current["temperature"]
        wind = current["windspeed"]

        # дополнительные данные (берём первый час)
        humidity = weather_data["hourly"]["relativehumidity_2m"][0]
        clouds = weather_data["hourly"]["cloudcover"][0]

        message = (
            f"🌤 Погода в городе {city}\n\n"
            f"🌡 Температура: {temp}°C\n"
            f"🤔 Ощущается как: ~{temp}°C\n"
            f"💧 Влажность: {humidity}%\n"
            f"🌬 Ветер: {wind} км/ч\n"
            f"☁️ Облачность: {clouds}%"
        )

    except requests.exceptions.Timeout:
        message = "⏳ Сервер не отвечает (таймаут)"
    except Exception as e:
        message = f"❌ Ошибка: {e}"

    await update.message.reply_text(message)


def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, weather))

    print("Бот запущен...")

    app.run_polling()


if __name__ == "__main__":
    main()
