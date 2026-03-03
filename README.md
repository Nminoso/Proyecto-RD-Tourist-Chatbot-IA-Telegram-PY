 RD Tourist AI Bot
Asistente virtual inteligente para Telegram diseñado para ayudar a turistas a explorar la República Dominicana. Utiliza Llama 3 (Groq) para recomendaciones personalizadas y geolocalización en tiempo real.

📦 Archivos del Proyecto
bot.py – Aplicación principal del bot (Python asíncrono).

.env – Variables de entorno para Tokens y API Keys (No subir a Git).

requirements.txt – Dependencias del proyecto (Versiones estables).

.gitignore – Configuración para excluir archivos sensibles y basura.

README.md – Guía de configuración y uso.

🧰 Requisitos
Python 3.11.x (Recomendado)

Windows, macOS, o Linux.

Telegram Bot Token (Obtenido de @BotFather).

Groq API Key (Obtenida de Groq Cloud).

⚠️ Nota de Compatibilidad

Este proyecto ha sido testeado con Python 3.11.9.

Se recomienda evitar Python 3.12+ en Windows para prevenir conflictos de dependencias con algunas librerías de red.

⚙️ Configuración (Ambiente Virtual)
Se recomienda encarecidamente el uso de un entorno virtual para mantener las dependencias aisladas.

1. Clonar y preparar carpeta
Crea tu carpeta de proyecto y coloca los archivos proporcionados.

2. Crear y activar ambiente virtual
Windows (PowerShell):

PowerShell
py -3.11 -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
macOS / Linux (bash/zsh):

Bash
python3.11 -m venv venv
source venv/bin/activate
python -m pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
3. Configurar variables de entorno
Crea un archivo llamado .env en la raíz del proyecto con el siguiente formato:

Fragmento de código
TELEGRAM_TOKEN=tu_telegram_bot_token_aqui
GROQ_API_KEY=tu_groq_api_key_aqui
🚀 Ejecución del Bot
Una vez configurado el .env y con el ambiente virtual activo, ejecuta:

Bash
python bot.py
🛠️ Funcionalidades Incluidas
Menú Interactivo: Botones de selección rápida para Playas, Montaña y Comida.

Geolocalización: El bot recibe tu ubicación GPS y te recomienda lugares cercanos en RD.

IA Generativa: Respuestas dinámicas con jerga dominicana y enlaces directos a Google Maps.