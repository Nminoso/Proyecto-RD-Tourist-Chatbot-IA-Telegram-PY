# 🇪🇸 VERSIÓN EN ESPAÑOL

# RD Tourist AI Bot 🇩🇴
Asistente virtual inteligente para Telegram diseñado para ayudar a turistas a explorar la República Dominicana. Utiliza Llama 3 (vía Groq) para recomendaciones personalizadas, geolocalización en tiempo real, consultas de clima, tasas de cambio y respuestas conscientes del tiempo local.

---

## ✨ Características Principales
- **Recomendaciones Inteligentes:** Rutas turísticas, playas, montañas y gastronomía dominicana.
- **Conciencia Temporal (UTC-4):** El bot sabe la hora exacta en RD para recomendar actividades adecuadas (ej. desayunos vs. vida nocturna).
- **Servicios en Tiempo Real:** - ☀️ Clima local (vía Open-Meteo).
  - 💵 Tasa de cambio USD a DOP (vía ExchangeRate-API).
- **Seguridad Robusta:** Enmascaramiento de tokens en consola, Secret Token para Webhooks y filtrado de eventos permitidos.
- **Entornos Flexibles:** Soporta modo `Polling` para pruebas locales y `Webhook` para despliegue en la nube (Render).

---

## 📦 Archivos del Proyecto
- `rdbot.py` – Aplicación principal del bot (Python asíncrono con seguridad reforzada).
- `.env` – Variables de entorno para Tokens, API Keys y configuración de entorno (No subir a Git).
- `requirements.txt` – Dependencias del proyecto (Versiones estables, incluye soporte para webhooks y requests).
- `.gitignore` – Configuración para excluir archivos sensibles y basura.
- `README.md` – Guía de configuración y uso.

---

## 🧰 Requisitos
- **Python 3.11.x (Recomendado)**
- Windows, macOS, o Linux.
- Telegram Bot Token (Obtenido de @BotFather).
- Groq API Key (Obtenida de Groq Cloud).
- Cuenta en Render (Opcional, para alojamiento en la nube).

---

## ⚠️ Nota de Compatibilidad

Este proyecto ha sido testeado con **Python 3.11.9**.

- Se recomienda evitar Python 3.12+ en Windows para prevenir conflictos de dependencias con algunas librerías de red.

---

## ⚙️ Configuración (Ambiente Virtual)

- Se recomienda encarecidamente el uso de un entorno virtual para mantener las dependencias aisladas.

### 1. Clonar y preparar carpeta
- Crea tu carpeta de proyecto y coloca los archivos proporcionados.

### 2. Crear y activar ambiente virtual

**Windows (PowerShell):**
```powershell
py -3.11 -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

**macOS / Linux (bash/zsh):**
```
python3.11 -m venv venv
source venv/bin/activate
python -m pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```
### 3. Configurar variables de entorno
- Crea un archivo llamado `.env` en la raíz del proyecto con el siguinete formato:

```
TELEGRAM_TOKEN=tu_token_de_telegram_aqui
GROQ_API_KEY=tu_api_key_de_groq_aqui
ENTORNO=local
# Las siguientes variables son exclusivas para producción (Render)
URL_RENDER=[https://tu-app.onrender.com](https://tu-app.onrender.com)
WEBHOOK_SECRET=TuContraseñaSecretaParaWebhook123
```
Nota: Para ejecutar localmente en tu PC, asegúrate de que `ENTORNO=local` para activar el modo Polling.


---

### Versión en Inglés (`README_EN.md`)


# RD Tourist AI Bot 🇩🇴
Smart virtual assistant for Telegram designed to help tourists explore the Dominican Republic. It uses Llama 3 (via Groq) for personalized recommendations, real-time geolocation, weather queries, exchange rates, and time-aware responses.

---

## ✨ Key Features
- **Smart Recommendations:** Tourist routes, beaches, mountains, and Dominican gastronomy.
- **Time Awareness (UTC-4):** The bot knows the exact time in DR to recommend appropriate activities (e.g., breakfast vs. nightlife).
- **Real-Time Services:** - ☀️ Local weather (via Open-Meteo).
  - 💵 USD to DOP exchange rate (via ExchangeRate-API).
- **Robust Security:** Token masking in console logs, Secret Token for Webhooks, and allowed events filtering.
- **Flexible Environments:** Supports `Polling` mode for local testing and `Webhook` mode for cloud deployment (Render).

---

## 📦 Project Files
- `rdbot.py` – Main bot application (Asynchronous Python with hardened security).
- `.env` – Environment variables for Tokens, API Keys, and environment config (Do not commit to Git).
- `requirements.txt` – Project dependencies (Stable versions, includes webhook and requests support).
- `.gitignore` – Configuration to exclude sensitive and junk files.
- `README_EN.md` – Setup and usage guide.

---

## 🧰 Requirements
- **Python 3.11.x (Recommended)**
- Windows, macOS, or Linux.
- Telegram Bot Token (Obtained from @BotFather).
- Groq API Key (Obtained from Groq Cloud).
- Render Account (Optional, for cloud hosting).

---

## ⚠️ Compatibility Note

This project has been tested with **Python 3.11.9**.

- It is recommended to avoid Python 3.12+ on Windows to prevent dependency conflicts with certain network libraries.

---

## ⚙️ Setup (Virtual Environment)

- Using a virtual environment is strongly recommended to keep dependencies isolated.

### 1. Clone and prepare folder
- Create your project folder and place the provided files inside.

### 2. Create and activate virtual environment

**Windows (PowerShell):**
```powershell
py -3.11 -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```
macOS / Linux (bash/zsh):
```
python3.11 -m venv venv
source venv/bin/activate
python -m pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```
### 3. Configure environment variables
Create a file named .env in the root of the project with the following format:
```
TELEGRAM_TOKEN=your_telegram_token_here
GROQ_API_KEY=your_groq_api_key_here
ENTORNO=local
# The following variables are exclusive for production (Render)
URL_RENDER=[https://your-app.onrender.com](https://your-app.onrender.com)
WEBHOOK_SECRET=YourSecretWebhookPassword123
```
Note: To run locally on your PC, make sure ENTORNO=local is set to activate Polling mode.
