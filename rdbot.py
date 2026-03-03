import os
import logging
import threading
from flask import Flask
from dotenv import load_dotenv
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from groq import Groq

# --- CONFIGURACIÓN DEL SERVIDOR WEB (PARA RENDER) ---
app_web = Flask(__name__)

@app_web.route('/')
def index():
    return "¡El bot turístico de RD está activo y funcionando! 🇩🇴"

def run_web():
    # Render asigna dinámicamente un puerto en la variable 'PORT'
    port = int(os.environ.get("PORT", 10000))
    app_web.run(host="0.0.0.0", port=port)

# --- CONFIGURACIÓN DEL BOT DE TELEGRAM ---
# Cargar variables de entorno desde .env (en local) o desde el panel de Render
load_dotenv()
TOKEN = os.getenv("TELEGRAM_TOKEN")
GROQ_KEY = os.getenv("GROQ_API_KEY")

# Inicializar IA
cliente = Groq(api_key=GROQ_KEY)

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    boton_gps = KeyboardButton("📍 Compartir mi ubicación actual", request_location=True)
    botones = [
        [boton_gps],
        ['🏖️ Playas', '⛰️ Montañas'],
        ['🍴 Comida Dominicana', '🏛️ Historia y Museos']
    ]
    markup = ReplyKeyboardMarkup(botones, resize_keyboard=True)

    await update.message.reply_text(
        f"¡Dímelo, {update.effective_user.first_name}! 🇩🇴\n"
        "Soy tu guía experto. ¿Qué quieres explorar hoy en Quisqueya?",
        reply_markup=markup
    )

async def manejar_ubicacion(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lat, lon = update.message.location.latitude, update.message.location.longitude
    map_link = f"https://www.google.com/maps?q={lat},{lon}"
    
    prompt = f"El turista está en {lat}, {lon}. Recomienda 3 lugares cercanos en RD y usa jerga dominicana amigable."
    
    try:
        res = cliente.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "system", "content": prompt}]
        )
        await update.message.reply_text(f"📍 Estás aquí: {map_link}\n\n{res.choices[0].message.content}")
    except Exception as e:
        await update.message.reply_text("¡Epa! No pude leer tu GPS ahora mismo. 🥥")

async def responder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message.text
    system_prompt = "Eres 'RD Guide Bot'. Responde siempre sobre turismo en RD y añade enlaces de Google Maps."
    
    try:
        res = cliente.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": msg}]
        )
        await update.message.reply_text(res.choices[0].message.content)
    except Exception:
        await update.message.reply_text("Hubo un error con la conexión a la IA. 🌴")

if __name__ == '__main__':
    # 1. Iniciar el servidor web de Flask en un hilo paralelo
    hilo_web = threading.Thread(target=run_web)
    hilo_web.start()

    # 2. Construir e iniciar el bot de Telegram
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.LOCATION, manejar_ubicacion))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), responder))
    
    print("Bot turístico RD y Servidor Web corriendo... 🇩🇴")
    app.run_polling()