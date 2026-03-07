import os
import logging
from dotenv import load_dotenv
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.constants import ParseMode # <-- Importante para leer HTML
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from groq import Groq

# --- CONFIGURACIÓN DE VARIABLES ---
load_dotenv()
TOKEN = os.getenv("TELEGRAM_TOKEN")
GROQ_KEY = os.getenv("GROQ_API_KEY")
RENDER_URL = os.getenv("URL_RENDER", "https://proyecto-rd-tourist-chatbot-ia-telegram.onrender.com")

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
    
    # Prompt estricto para ubicación
    prompt = (
        f"El turista está en {lat}, {lon}. Recomienda 3 lugares cercanos en RD. "
        "REGLAS ESTRICTAS: "
        "1. NO uses asteriscos ni símbolos raros para resaltar texto. "
        "2. Para cada lugar, DEBES añadir un enlace EXACTAMENTE con este formato HTML: "
        "<a href='AQUÍ_LA_URL'>Ver en Google map 📍</a>. "
        "Usa jerga dominicana amigable."
    )
    
    try:
        res = cliente.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "system", "content": prompt}]
        )
        
        # Limpieza forzada por si la IA envía asteriscos
        texto_limpio = res.choices[0].message.content.replace("*", "").replace("#", "")
        
        await update.message.reply_text(
            f"📍 Estás aquí: <a href='{map_link}'>Ver tu ubicación actual 📍</a>\n\n{texto_limpio}",
            parse_mode=ParseMode.HTML # Le dice a Telegram que procese los enlaces
        )
    except Exception as e:
        logging.error(f"Error en GPS: {e}")
        await update.message.reply_text("¡Epa! No pude leer tu GPS ahora mismo. 🥥")

async def responder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message.text
    
    # Prompt estricto para texto general
    system_prompt = (
        "Eres 'RD Guide Bot'. Responde siempre sobre turismo en RD. "
        "REGLAS ESTRICTAS: "
        "1. NO uses negritas, NO uses asteriscos, NO uses símbolos raros. Texto limpio y directo. "
        "2. Siempre que menciones un lugar, genera su enlace a Google Maps usando EXACTAMENTE "
        "este formato HTML: <a href='URL_DEL_LUGAR'>Ver en Google map 📍</a>."
    )
    
    try:
        res = cliente.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": msg}]
        )
        
        # Limpieza forzada de asteriscos y símbolos markdown
        texto_limpio = res.choices[0].message.content.replace("*", "").replace("#", "")
        
        await update.message.reply_text(
            texto_limpio, 
            parse_mode=ParseMode.HTML # Convierte las etiquetas <a> en enlaces clickeables
        )
    except Exception as e:
        logging.error(f"Error en IA: {e}")
        await update.message.reply_text("Hubo un error con la conexión a la IA. 🌴")

if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 10000))
    
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.LOCATION, manejar_ubicacion))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), responder))
    
    print("Iniciando bot turístico con formato limpio y enlaces HTML... 🇩🇴")
    
    app.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        webhook_url=f"{RENDER_URL}/{TOKEN}",
        url_path=TOKEN
    )