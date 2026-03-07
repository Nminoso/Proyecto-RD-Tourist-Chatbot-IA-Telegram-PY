import os
import logging
import requests
from datetime import datetime, timezone, timedelta
from collections import defaultdict
from dotenv import load_dotenv
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.constants import ParseMode
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from groq import Groq

# --- 1. CONFIGURACIÓN DE VARIABLES Y ARRANQUE SEGURO ---
load_dotenv()
TOKEN = os.getenv("TELEGRAM_TOKEN")
GROQ_KEY = os.getenv("GROQ_API_KEY")
RENDER_URL = os.getenv("URL_RENDER", "https://proyecto-rd-tourist-chatbot-ia-telegram.onrender.com")
ENTORNO = os.getenv("ENTORNO", "produccion") 
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET") 

if not TOKEN or not GROQ_KEY:
    print("❌ ERROR DE SEGURIDAD: Faltan credenciales en el entorno. Apagando...")
    exit(1)

# --- 2. FILTRO DE SEGURIDAD MEJORADO PARA LA TERMINAL ---
class TokenRedactorFilter(logging.Filter):
    def filter(self, record):
        msg = record.getMessage() 
        if TOKEN in msg or GROQ_KEY in msg:
            record.msg = msg.replace(TOKEN, "***TOKEN_TELEGRAM_OCULTO***").replace(GROQ_KEY, "***API_GROQ_OCULTA***")
            record.args = () 
        return True

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger()
for handler in logger.handlers:
    handler.addFilter(TokenRedactorFilter())

logging.getLogger("httpx").setLevel(logging.WARNING)

# Inicializar IA
cliente = Groq(api_key=GROQ_KEY)

# --- MEMORIA CONVERSACIONAL ---
historial_usuarios = defaultdict(list)
LIMITE_MENSAJES = 14 

def actualizar_historial(user_id, rol, contenido):
    historial_usuarios[user_id].append({"role": rol, "content": contenido})
    if len(historial_usuarios[user_id]) > LIMITE_MENSAJES:
        historial_usuarios[user_id] = historial_usuarios[user_id][2:]

def obtener_prompt_sistema():
    """Genera el prompt dinámico inyectando la hora real de República Dominicana."""
    # Calcular la hora exacta en RD (UTC-4)
    zona_horaria_rd = timezone(timedelta(hours=-4))
    hora_actual_rd = datetime.now(zona_horaria_rd).strftime("%I:%M %p")
    dia_actual_rd = datetime.now(zona_horaria_rd).strftime("%A")
    
    # Diccionario simple para traducir el día al español
    dias_es = {"Monday": "Lunes", "Tuesday": "Martes", "Wednesday": "Miércoles", "Thursday": "Jueves", "Friday": "Viernes", "Saturday": "Sábado", "Sunday": "Domingo"}
    dia_es = dias_es.get(dia_actual_rd, dia_actual_rd)

    return (
        f"Eres 'DR Guide Bot', un experto guía turístico de la República Dominicana. "
        f"RELOJ INTERNO DEL SISTEMA: Hoy es {dia_es} y la hora local en RD es {hora_actual_rd}. "
        "Tus respuestas deben ser cálidas y usar jerga dominicana educada (ej. '¡Qué lo qué!', 'nítido', 'jevi'). "
        "REGLAS ESTRICTAS E INQUEBRANTABLES: "
        "1. CERO MALAS PALABRAS o expresiones vulgares. "
        "2. NO uses Markdown (NO asteriscos **, NO hashtags #). "
        "3. NUNCA INVENTES URLs. Para crear el enlace de Google Maps, DEBES construir una URL de búsqueda oficial. "
        "Convierte el nombre del lugar en un enlace usando este formato HTML: "
        "<a href='https://www.google.com/maps/search/?api=1&query=NOMBRE+DEL+LUGAR+REPUBLICA+DOMINICANA'>Nombre del Lugar 📍</a>. "
        "Asegúrate de reemplazar los espacios en blanco del nombre del lugar con el signo '+' en la URL. "
        "4. CONTEXTO TEMPORAL: Adapta siempre tus recomendaciones a la hora local actual. Si es de mañana, recomienda desayunos, playas o museos. Si es de noche (después de las 7 PM), recomienda cenas, bares o vida nocturna. "
        "5. PROACTIVIDAD: Si el turista pide una recomendación genérica ('dime un lugar para ir') y es de noche o madrugada, pregúntale amablemente si el plan es para salir 'ahora mismo' o si está planificando para el día siguiente, así ajustas tus sugerencias. "
        "6. Si te piden Hospitales o Clínicas, recomiéndales usar el botón '📍 Compartir mi ubicación' para darles los más cercanos, y menciónales centros seguros (ej. Hospiten, CEDIMAT)."
    )

def obtener_clima_rd():
    try:
        base_url = "https://api.open-meteo.com/v1/forecast?current_weather=true"
        pc = requests.get(f"{base_url}&latitude=18.58&longitude=-68.40", timeout=3).json()
        sd = requests.get(f"{base_url}&latitude=18.48&longitude=-69.93", timeout=3).json()
        pp = requests.get(f"{base_url}&latitude=19.79&longitude=-70.68", timeout=3).json()
        
        return (
            f"\n\n[INFO DE SISTEMA EN TIEMPO REAL: Temperaturas actuales: "
            f"Punta Cana: {pc['current_weather']['temperature']}°C, "
            f"Santo Domingo: {sd['current_weather']['temperature']}°C, "
            f"Puerto Plata: {pp['current_weather']['temperature']}°C. "
            f"Usa estas temperaturas exactas para responderle al usuario de forma amigable.]"
        )
    except Exception as e:
        logger.error(f"Error al obtener clima: {e}")
        return (
            "\n\n[INFO DE SISTEMA: El API del clima falló. Dile al usuario con simpatía "
            "que no tienes la temperatura exacta en la mano, pero recomiéndale llevar ropa ligera "
            "porque en RD casi siempre hace un clima tropical riquísimo (entre 28°C y 32°C).]"
        )

def obtener_tasa_cambio():
    try:
        response = requests.get("https://api.exchangerate-api.com/v4/latest/USD", timeout=3).json()
        tasa_dop = response['rates']['DOP']
        return (
            f"\n\n[INFO DE SISTEMA EN TIEMPO REAL: La tasa de cambio oficial actual es de "
            f"1 USD (Dólar) = {tasa_dop} DOP (Pesos Dominicanos). "
            f"Usa esta tasa exacta para responderle al turista de forma útil y ayúdalo si quiere calcular un monto.]"
        )
    except Exception as e:
        logger.error(f"Error al obtener tasa de cambio: {e}")
        return (
            "\n\n[INFO DE SISTEMA: El API de moneda falló. Dile al turista que la tasa promedio ronda los "
            "59 a 60 pesos por cada dólar, pero que siempre verifique en una casa de cambio o banco.]"
        )

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    historial_usuarios[user_id].clear() 
    
    boton_gps = KeyboardButton("📍 Compartir mi ubicación", request_location=True)
    botones = [
        [boton_gps],
        ['🏖️ Playas', '⛰️ Montañas', '🏞️ Ríos'],
        ['🍴 Comida Dominicana', '🏛️ Historia y Museos'],
        ['🏥 Hospitales y Clínicas', '☀️ Clima Actual'],
        ['💵 Tasa de Cambio', '🆘 Emergencia (SOS)']
    ]
    markup = ReplyKeyboardMarkup(botones, resize_keyboard=True)

    await update.message.reply_text(
        f"¡Dímelo, {update.effective_user.first_name}! 🇩🇴\n\n"
        "Soy tu guía experto. ¿Qué quieres explorar hoy en Quisqueya la Bella?\n\n"
        "💡 <i>Tip: Escribe /olvidar si quieres cambiar de tema radicalmente, o /sos para emergencias.</i>",
        reply_markup=markup,
        parse_mode=ParseMode.HTML
    )

async def emergencia(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texto_sos = (
        "🚨 <b>NÚMEROS DE EMERGENCIA - REPÚBLICA DOMINICANA</b> 🚨\n\n"
        "• <b>Sistema Nacional de Emergencias (Ambulancia, Policía, Bomberos):</b> 911\n"
        "• <b>CESTUR (Policía Turística):</b> 809-222-2026\n"
        "• <b>Policía Nacional (Central):</b> 809-682-2151\n"
        "• <b>Defensa Civil:</b> 809-472-8614\n"
        "• <b>Cruz Roja Dominicana:</b> 809-334-4545\n\n"
        "<i>Por favor, comunícate inmediatamente con el 911 si te encuentras en una situación de peligro inminente. ¡Mantente a salvo!</i>"
    )
    await update.message.reply_text(texto_sos, parse_mode=ParseMode.HTML)

async def olvidar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    historial_usuarios[user_id].clear()
    
    await update.message.reply_text(
        "¡Nítido! Ya borré el cassette 📼. Empecemos de cero. ¿Pa' dónde vamos ahora?",
        parse_mode=ParseMode.HTML
    )

async def manejar_ubicacion(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    lat, lon = update.message.location.latitude, update.message.location.longitude
    map_link = f"https://www.google.com/maps?q={lat},{lon}"
    
    mensaje_usuario = f"Acabo de enviar mis coordenadas exactas: {lat}, {lon}. Basado en nuestra conversación, recomiéndame 3 lugares cercanos o dime qué hay a mi alrededor."
    actualizar_historial(user_id, "user", mensaje_usuario)
    
    mensajes_ia = [{"role": "system", "content": obtener_prompt_sistema()}]
    mensajes_ia.extend(historial_usuarios[user_id]) 
    
    try:
        res = cliente.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=mensajes_ia,
            temperature=0.7
        )
        
        texto_limpio = res.choices[0].message.content.replace("*", "").replace("#", "")
        actualizar_historial(user_id, "assistant", texto_limpio)
        
        await update.message.reply_text(
            f"📍 <a href='{map_link}'>Ver tu ubicación actual</a>\n\n{texto_limpio}",
            parse_mode=ParseMode.HTML
        )
    except Exception as e:
        logger.error(f"Error en GPS: {e}")
        await update.message.reply_text("¡Epa! No pude procesar tu GPS ahora mismo. 🥥")

async def responder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    msg = update.message.text
    
    actualizar_historial(user_id, "user", msg)
    
    palabras_clima = ["clima", "temperatura", "tiempo", "llover", "lluvia", "sol", "calor", "frío"]
    palabras_moneda = ["dólar", "dolar", "peso", "cambio", "tasa", "moneda", "convertir", "precio"]
    
    prompt_base = obtener_prompt_sistema()
    
    if any(palabra in msg.lower() for palabra in palabras_clima):
        prompt_base += obtener_clima_rd()
        
    if any(palabra in msg.lower() for palabra in palabras_moneda):
        prompt_base += obtener_tasa_cambio()
    
    mensajes_ia = [{"role": "system", "content": prompt_base}]
    mensajes_ia.extend(historial_usuarios[user_id])
    
    try:
        res = cliente.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=mensajes_ia,
            temperature=0.7 
        )
        
        texto_limpio = res.choices[0].message.content.replace("*", "").replace("#", "")
        actualizar_historial(user_id, "assistant", texto_limpio)
        
        await update.message.reply_text(texto_limpio, parse_mode=ParseMode.HTML)
    except Exception as e:
        logger.error(f"Error en IA: {e}")
        await update.message.reply_text("La conexión está un chin lenta. ¡Inténtalo de nuevo! 🌴")

if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 10000))
    app = ApplicationBuilder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("olvidar", olvidar)) 
    app.add_handler(CommandHandler(["sos", "emergencia"], emergencia))
    app.add_handler(MessageHandler(filters.Regex(r'^🆘 Emergencia \(SOS\)$'), emergencia))
    app.add_handler(MessageHandler(filters.LOCATION, manejar_ubicacion))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), responder))
    
    if ENTORNO == "local":
        print("Iniciando bot en modo LOCAL (Polling seguro)... 🇩🇴")
        app.run_polling(allowed_updates=[Update.MESSAGE])
    else:
        print("Iniciando bot en modo NUBE (Webhook protegido)... 🇩🇴")
        app.run_webhook(
            listen="0.0.0.0",
            port=PORT,
            webhook_url=f"{RENDER_URL}/{TOKEN}",
            url_path=TOKEN,
            secret_token=WEBHOOK_SECRET, 
            allowed_updates=[Update.MESSAGE]
        )