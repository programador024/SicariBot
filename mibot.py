#Aqui importamos el token
from config import *
import os
#Para trabajar con la AI de Telegram
import telebot
telebot.logger.setLevel(__import__('logging').DEBUG)
from telebot.types import (BotCommand, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton)
#Importación optimizada y botones inline
from datetime import datetime
#Importar datetime para fecha/hora
from datetime import datetime
#Crear la base de datos para los registro de los usuarios
import sqlite3
#Para zona horarica de cualquier pais
import pytz
#Para la descarga de imagen, musica, texto, sticker
import re
import logging
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler
from googleapiclient.discovery import build
from bs4 import BeautifulSoup
import requests
#from pytube import YouTube 
from pydub import AudioSegment
#from yt_dlp import YoutubeDL
from PIL import Image  # Para redimensionar y convertir la imagen

#Configuración de la API de Google Custom Search
API_KEY = "AIzaSyC3LdsqVZm45n2bUKgeuWP2dHHKYOKYV6w" #ID de Google Cloud Console
SEARCH_ENGINE_ID = "a50b16cd1fe4b4a45" #ID de Custom Search
SEARCH_URL = "https://www.googleapis.com/customsearch/v1"

# Instanciar el bot en Telegram
bot = telebot.TeleBot(TELEGRAM_TOKEN) 
# Conectar con la base de datos SQLite(se creara si no existe)
conn = sqlite3.connect("usuarios.db", check_same_thread=False)
cursor = conn.cursor()

# Crear la tabla de usuarios si no existe
cursor.execute('''CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    chat_id INTEGER UNIQUE,
    username TEXT,
    nombre_completo TEXT,
    fecha_nacimiento TEXT,
    rol TEXT,
    pais TEXT,
    foto TEXT
)''')

# Crear la tabla de calificaciones si no existe
cursor.execute(''' CREATE TABLE IF NOT EXISTS calificaciones (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    chat_id INTEGER UNIQUE,
    calificacion INTEGER
 )''')

# Guardar cambios y cerrar conexión
conn.commit()
conn.close()
print("Base de datos creada correctamente.")

# Diccionario para almacenar datos de los usuarios
user_data = {}

# Diccionario para rastrear el estado del usuario para el sticker
esperando_imagen = {}

#Funcion para obtener la hora local del usuario
def obtener_hora_local(pais):
    #Diccionario de paises con sus zonas horarias
    zonas_horarias = {
        "Argentina": "America/Argentina/Buenos_Aires",
        "México": "America/Mexico_City",
        "Colombia": "America/Bogota",
        "España": "Europe/Madrid",
        "Chile": "America/Santiago",
        "Perú": "America/Lima",
        "Venezuela": "America/Caracas",
        "Alemania": "Europe/Berlín",
        "Bolivia": "America/Bolivia/La_Paz",
        "Brasil": "America/Brasilia",
        "Canadá": "America/Ottawa",
        "Cuba": "America/La_Habana",
        "Dominica": "America/Roseau",
        "Ecuador": "America/Quito",
        "El Salvador": "America/San_Salvador",
        "España": "Europa/Madrid",
        "Estados Unidos": "America/Whashington_D.C.",
        "Guatemala": "America/Ciudad_de_Guatemala",
        "Honduras": "Tegucigalpa",
        "Japón": "Asia/Tokio",
        "Nicaragua": "America/Managua",
        "Panamá": "America/Ciudad_de_Panamá",
        "Paraguay": "America/Asunción",
        "República Dominicana": "America/Santo_Domingo",
        "Rusia": "Europe/Moscú",
        "Paraguay": "America/Montevideo",     
    }

    zona_horaria = zonas_horarias.get(pais, "UTC") #Si no encuentra el pais, usa UTC
    zona = pytz.timezone(zona_horaria)
    ahora = datetime.now(zona)
    return ahora.strftime("%d/%m/%Y 🕔  %H:%M:%S") 

# Configurar los comandos disponibles en el menú
bot.set_my_commands([
    BotCommand("start", "Inicia el bot"),
    BotCommand("menu", "Lista de comandos y ayuda"),
    BotCommand("creador", "Información del creador"),
    BotCommand("canaltelegram", "Canal de Telegram"),
    BotCommand("canalyoutube", "Canal de YouTube"),
    BotCommand("paginaweb", "Página web del creador"),
    BotCommand("registro", "Registrarte con el bot"),
    BotCommand("perfil", "Ver tu perfil registrado"),
    BotCommand("deleteusuario", "Eliminar tu perfil registrado"),
    BotCommand("mtmanager", "Aplicación para editar strings y codigos de mods"),
    BotCommand("mtmanagerbeta", "Aplicación para editar cadenas y codigosde Apps de manera mas avanzada"),
    BotCommand("apkeditorpro", "Aplicación para editar tanto el codigo como el diseño de los mods"),
    BotCommand("apktoolm", "Aplicación para cambiar tanto el nombre de los mods como su imagen de log"),
    BotCommand("telegrampremium", "Telegram con funciones de premium desbloqueadas, modificado por su servidor"),
    BotCommand("imagen", "Comando /imagen + Nombre"),
    BotCommand("musica", "Comando /musica + Nombre"),
    BotCommand("video", "Comando /video + Nombre"),
    BotCommand("aibuscar", "Comando /aibuscar + Texto"),
    BotCommand("aisticker", "Crear sticker"),
])

#Agregar botones de reply keyboard
button1 = KeyboardButton("🙍‍  Cuenta")
button2 = KeyboardButton("⚙️  Ayuda")
button3 = KeyboardButton("🛠️  Soporte")
button4 = KeyboardButton("📝  Calificar")
button5 = KeyboardButton("📊 Ver Calificaciones")
keyboard1 = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
keyboard1.row(button1, button2)
keyboard1.row(button3, button4)
keyboard1.row(button5)

#Responder al comando /start
@bot.message_handler(commands=["start"])
def cmd_start(message):
    username = message.from_user.username or "usuario"
    bot.reply_to(message, f"Hola @{username}, soy SicarioBot, tu asistente virtual. ¿En qué te puedo ayudar?\n\n Ejecuta /menu para ver los comandos.", reply_markup=keyboard1)

#Responder al comando /menu
@bot.message_handler(commands=["menu"])
def cmd_menu(message):
    chat_id = message.chat.id

    #Consultar el pais del usuario desde la base de datos
    with obtener_conexion() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT pais FROM usuarios WHERE chat_id = ?", (chat_id,))
        resultado = cursor.fetchone()
    pais = resultado[0] if resultado else "UTC" #Si no hay pais se usa UTC
    fecha_hora = obtener_hora_local(pais)

    menu_text = f"""
<b>🤖 MENÚ SICARIOBOT 🤖</b>
📅 {fecha_hora}    
Comandos disponibles:
/start - Inicia el bot
/menu - Lista de comandos
/creador - Info del creador
📱 Redes Sociales:
/canaltelegram - Canal de Telegram
/canalyoutube - Canal de YouTube
/paginaweb - Página web
📝 Registro:
/registro - Registrarte
/perfil - Ver tu perfil
/deleteusuario - Eliminar perfil
🕹️ Apps Premium:
/mtmanager - Editar strings y códigos
/mtmanagerbeta - Versión avanzada
/apkeditorpro - Editar código y diseño
/apktoolm - Cambiar nombre e icono
/telegrampremium - Telegram prem
🎬Descargar Multimedia e IA🤖:
/imagen + Nombre
/musica + Nombre
/video + Nombre
/aibuscar + Texto
/aisticker - Crear sticker
    """
    #Crear botón "Ver canal"
    keyboard = InlineKeyboardMarkup()
    boton_canal = InlineKeyboardButton("📢 VER CANAL", url="https://t.me/mds_inmunes")
    keyboard.add(boton_canal)
    with open("imagenes/sicaribot_menu2.jpg", "rb") as photo:
        bot.send_photo(message.chat.id, photo, caption=menu_text, parse_mode='HTML', reply_markup=keyboard)
        bot.send_message("Selecciona una obción:", reply_markup=keyboard1)

# Manejar respuestas a los botones del teclado
@bot.message_handler(func=lambda message: message.text in ["🙍‍  Cuenta", "⚙️  Ayuda", "🛠️  Soporte", "📝  Calificar", "📊 Ver Calificaciones"])
def cmd_kb_answer(message):
    if message.text == "🙍‍  Cuenta":
        bot.reply_to(message, "Digita los siguientes comandos, para lo que desees hacer en tu cuenta. \n\n/registro - Registrarte\n\n/perfil - Ver tu perfil\n\n/deleteusuario - Eliminar perfil")
    elif message.text == "⚙️  Ayuda":
        bot.reply_to(message, "Para el uso del bot, digita los siguientes comandos. \n\n/start - Iniciar el bot\n\n/menu - Ver el menu completo\n\n/creador - Información del creador")
    elif message.text == "🛠️  Soporte":
        bot.reply_to(message, "Puedes contactar a soporte del bot, para cualquier cosa o duda.\n\nEnvia un mensaje a soporte al siguiente correo: teamzetasprivatev1@gmail.com")
    elif message.text == "📝  Calificar":
        markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        botones = [KeyboardButton(str(i)) for i in range(1, 11)]  # Botones del 1 al 10
        markup.row(*botones[:5])  # Primera fila con 5 números
        markup.row(*botones[5:])  # Segunda fila con los otros 5
        markup.row(KeyboardButton("❌ Cancelar"))  # Botón de cancelar en una fila aparte
        bot.reply_to(message, "Por favor, califica el bot del 1 al 10 o presiona '❌ Cancelar' ", reply_markup=markup)
    elif message.text == "📊 Ver Calificaciones":
        with sqlite3.connect("usuarios.db") as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT AVG(calificacion) FROM calificaciones")  # Promedio de calificaciones
            resultado = cursor.fetchone()
            promedio = resultado[0] if resultado[0] else 0  # Si no hay calificaciones, muestra 0
        bot.reply_to(message, f"📊 El bot tiene una calificación promedio de: {promedio:.1f}/10 ⭐")

# Guardar la calificación
@bot.message_handler(func=lambda message: message.text.isdigit() and 1 <= int(message.text) <= 10)
def guardar_calificacion(message):
    chat_id = message.chat.id
    calificacion = int(message.text)
    with sqlite3.connect("usuarios.db") as conn:
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS calificaciones (chat_id INTEGER PRIMARY KEY, calificacion INTEGER)")
        cursor.execute("INSERT OR REPLACE INTO calificaciones (chat_id, calificacion) VALUES (?, ?)", (chat_id, calificacion))
        conn.commit()
    # Eliminar el teclado de calificación
    bot.reply_to(message, f"¡Gracias por calificar con {calificacion}/10! ⭐,", reply_markup=ReplyKeyboardRemove())
    # Volver a mostrar el teclado principal
    mostrar_menu_principal(chat_id)

# Manejar la cancelación de la calificación
@bot.message_handler(func=lambda message: message.text == "❌ Cancelar")
def cancelar_calificacion(message):
    chat_id = message.chat.id

    # Eliminar el teclado de calificación
    bot.reply_to(message, "Calificación cancelada. Volviendo al menú principal...", reply_markup=ReplyKeyboardRemove())

    # Volver a mostrar el teclado principal
    mostrar_menu_principal(chat_id)

# Función para mostrar el teclado principal
def mostrar_menu_principal(chat_id):
    button1 = KeyboardButton("🙍‍  Cuenta")
    button2 = KeyboardButton("⚙️  Ayuda")
    button3 = KeyboardButton("🛠️  Soporte")
    button4 = KeyboardButton("📝  Calificar")
    button5 = KeyboardButton("📊 Ver Calificaciones")
    keyboard1 = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
    keyboard1.row(button1, button2)
    keyboard1.row(button3, button4)
    keyboard1.row(button5)  
    bot.send_message(chat_id, "Menú principal:", reply_markup=keyboard1)

#Responder al comando /creador
@bot.message_handler(commands=["creador"])
def cmd_creador(message):
    bot.reply_to(message, f"Fui creado por SicarioOfc, puedes contactarlo en sus redes en el apartado de Redes Sociales📱 que se muestra en /menu", reply_markup=keyboard1)

# Responder al comando /canaltelegram
@bot.message_handler(commands=["canaltelegram"])
def cmd_canaltelegram(message):
    bot.reply_to(message, "Mi Telegram es: https://t.me/mds_inmunes", reply_markup=keyboard1)

# Responder al comando /canalyoutube
@bot.message_handler(commands=["canalyoutube"])
def cmd_canalyoutube(message):
    bot.reply_to(message, "Mi YouTube es: https://www.youtube.com/@nms_sicario023", reply_markup=keyboard1)
 
# Responder al comando /paginaweb
@bot.message_handler(commands=["paginaweb"])
def cmd_paginaweb(message):
    bot.reply_to(message, "Mi Página Web es: https://teamzetasprivate.kesug.com/", reply_markup=keyboard1)      
         
#Obtener la conexión a la base de datos         
def obtener_conexion():
    return sqlite3.connect("usuarios.db", check_same_thread=False)
            

# Comando /registro
@bot.message_handler(commands=["registro"])
def cmd_registro(message):
    chat_id = message.chat.id
    with obtener_conexion() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM usuarios WHERE chat_id = ?", (chat_id,))
        conn.commit()
        if cursor.fetchone():
            bot.send_message(chat_id, "Ya estás registrado. Usa /perfil para ver tus datos.")
            return

    bot.send_message(chat_id, "¿Cuál es tu nombre completo?")
    bot.register_next_step_handler(message, obtener_nombre)

def obtener_nombre(message):
    chat_id = message.chat.id
    username = message.from_user.username or "usuario"
    nombre_completo = message.text
    bot.send_message(chat_id, "¿Cuál es tu fecha de nacimiento? (Formato: DD/MM/AAAA)")
    bot.register_next_step_handler(message, obtener_fecha, username, nombre_completo)

def obtener_fecha(message, username, nombre_completo):
    chat_id = message.chat.id
    try:
        fecha_nacimiento = datetime.strptime(message.text, "%d/%m/%Y").strftime("%Y-%m-%d")
        bot.send_message(chat_id, "¿Cuál es tu rol o hobby?")
        bot.register_next_step_handler(message, obtener_rol, username, nombre_completo, fecha_nacimiento)
    except ValueError:
        bot.send_message(chat_id, "Formato incorrecto. Usa DD/MM/AAAA.")
        bot.register_next_step_handler(message, obtener_fecha, username, nombre_completo)

def obtener_rol(message, username, nombre_completo, fecha_nacimiento):
    chat_id = message.chat.id
    rol = message.text
    bot.send_message(chat_id, "¿En qué país vives?")
    bot.register_next_step_handler(message, obtener_pais, username, nombre_completo, fecha_nacimiento, rol)

def obtener_pais(message, username, nombre_completo, fecha_nacimiento, rol):
    chat_id = message.chat.id
    pais = message.text
    bot.send_message(chat_id, "Ahora envíame una imagen para tu perfil (opcional).")
    bot.register_next_step_handler(message, obtener_imagen, username, nombre_completo, fecha_nacimiento, rol, pais)

def obtener_imagen(message, username, nombre_completo, fecha_nacimiento, rol, pais):
    chat_id = message.chat.id
    foto = message.photo[-1].file_id if message.content_type == "photo" else None

    with obtener_conexion() as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO usuarios (chat_id, username, nombre_completo, fecha_nacimiento, rol, pais, foto) VALUES (?, ?, ?, ?, ?, ?, ?)",
                       (chat_id, username, nombre_completo, fecha_nacimiento, rol, pais, foto))
        conn.commit()

    bot.send_message(chat_id, "✅ Registro completado. Usa /perfil para ver tus datos.")

    
    
import re

def escape_markdown_v2(text):
    """Función para escapar caracteres especiales en MarkdownV2"""
    escape_chars = r"_*[]()~`>#+-=|{}.!"
    return re.sub(r"([" + re.escape(escape_chars) + r"])", r"\\\1", text)

# Comando /perfil
@bot.message_handler(commands=["perfil"])
def cmd_perfil(message):
    chat_id = message.chat.id
    with obtener_conexion() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM usuarios WHERE chat_id = ?", (chat_id,))
        conn.commit()
        user = cursor.fetchone()

    if user:
        id, chat_id, username, nombre_completo, fecha_nacimiento, rol, pais, foto = user
        edad = calcular_edad(fecha_nacimiento)

        perfil = (
            f"✅ *Perfil Registrado*:\n"
            f"\\- *Nombre:* {escape_markdown_v2(nombre_completo)} \\(\\@{escape_markdown_v2(username)}\\)\n"
            f"\\- *Edad:* {escape_markdown_v2(str(edad))} años\n"
            f"\\- *Rol o Hobby:* {escape_markdown_v2(rol)}\n"
            f"\\- *País:* {escape_markdown_v2(pais)}"
        )

        if foto:
            bot.send_photo(chat_id, foto, caption=perfil, parse_mode="MarkdownV2")
        else:
            bot.send_message(chat_id, f"⚠️ No tienes foto de perfil. \n{perfil}", parse_mode="MarkdownV2")
    else:
        bot.send_message(chat_id, "No estás registrado❌. Usa /registro para comenzar.")


def calcular_edad(fecha_nacimiento):
    # Convertir la cadena 'YYYY-MM-DD' a un objeto datetime
    fecha_nacimiento = datetime.strptime(fecha_nacimiento, "%Y-%m-%d")
    hoy = datetime.today()
    
    # Calcular la edad correctamente
    edad = hoy.year - fecha_nacimiento.year - ((hoy.month, hoy.day) < (fecha_nacimiento.month, fecha_nacimiento.day))
    return edad


# Comando /deleteusuario
@bot.message_handler(commands=["deleteusuario"])
def cmd_deleteusuario(message):
    chat_id = message.chat.id
    with obtener_conexion() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM usuarios WHERE chat_id = ?", (chat_id,))
        conn.commit()
        
    bot.send_message(chat_id, "✅ Tu perfil ha sido eliminado. Usa /registro para crear uno nuevo.")


#Agregar función para restringir a las aplicaciones mediante el registro de los usuarios
def obtener_conexion():
    """Obtiene una conexión a la base de datos."""
    return sqlite3.connect("usuarios.db", check_same_thread=False)

def usuario_registrado(chat_id):
    """Verifica si un usuario está registrado en la base de datos."""
    with obtener_conexion() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM usuarios WHERE chat_id = ?", (chat_id,))
        return cursor.fetchone() is not None



#Agregar file de aplicaciones
def acceso_restringido(func):
    """ Decorador para restringir comandos a usuarios registrados """
    def wrapper(message):
        if usuario_registrado(message.chat.id):
            return func(message)
        else:
            bot.send_message(message.chat.id, "⚠️ Debes registrarte con /registro para usar este comando.", reply_markup=keyboard1)
    return wrapper

@bot.message_handler(commands=["mtmanager"])
@acceso_restringido
def cmd_mtmanager(message):
    with open("resources/MT Manager_2.18.0.apk", "rb") as mtmanager:
        bot.send_document(message.chat.id, mtmanager, reply_markup=keyboard1)

@bot.message_handler(commands=["mtmanagerbeta"])
@acceso_restringido
def cmd_mtmanagerbeta(message):
    with open("resources/MT Manager_2.14.5-clone.apk", "rb") as mtmanagerbeta:
        bot.send_document(message.chat.id, mtmanagerbeta, reply_markup=keyboard1)

@bot.message_handler(commands=["apkeditorpro"])
@acceso_restringido
def cmd_apkeditorpro(message):
    with open("resources/APK Editor Pro_1.10.0.apk", "rb") as apkeditorpro:
        bot.send_document(message.chat.id, apkeditorpro, reply_markup=keyboard1)

@bot.message_handler(commands=["apktoolm"])
@acceso_restringido
def cmd_apktoolm(message):
    with open("resources/Apktool M_2.4.0-250121.apk", "rb") as apktoolm:
        bot.send_document(message.chat.id, apktoolm, reply_markup=keyboard1)

    
@bot.message_handler(commands=["telegrampremium"])
@acceso_restringido
def cmd_telegrampremium(message):
    bot.reply_to(message, "Telegram PremiumV2: https://www.mediafire.com/file/nmqqa8ztye660i9/%25F0%259F%2594%25A5%25E2%2583%259F%25E2%2598%25A0%25EF%25B8%258ETelegram_Sicari%25F0%259F%258E%25ADV2.apk/file", reply_markup=keyboard1)    
    
# Función para buscar imágenes en Google
def buscar_imagen(query):
    service = build("customsearch", "v1", developerKey=API_KEY)
    res = service.cse().list(q=query, cx=SEARCH_ENGINE_ID, searchType="image").execute()
    if "items" in res:
        return res["items"][0]["link"]
    return None

# Comando /imagen
@bot.message_handler(commands=["imagen"])
@acceso_restringido
def cmd_imagen(message):
    query = message.text.replace("/imagen ", "")
    imagen_url = buscar_imagen(query)
    if imagen_url:
        bot.send_photo(message.chat.id, imagen_url, caption=f"Imagen encontrada para: {query}")
    else:
        bot.send_message(message.chat.id, "No encontré imágenes para esa búsqueda.")
        
# Función para buscar videos en YouTube mediante Google Custom Search
def buscar_video_youtube(query):
    try:
        service = build("customsearch", "v1", developerKey=API_KEY)
        res = service.cse().list(q=f"{query} site:youtube.com", cx=SEARCH_ENGINE_ID).execute()
        if "items" in res and len(res["items"]) > 0:
            return res["items"][0]["link"]
    except Exception as e:
        print(f"Error en la búsqueda de YouTube: {e}")
    return None

# Función para descargar el audio de YouTube y convertirlo a MP3
import yt_dlp
@bot.message_handler(commands=["musica"])
@acceso_restringido
def cmd_musica(message):
    chat_id = message.chat.id
    query = message.text.replace("/musica", "").strip()

    if not query:
        bot.reply_to(message, "❌ Debes escribir el nombre de la canción después de /musica")
        return

    bot.send_message(chat_id, f"🔍 Buscando y descargando: {query} ...")

    # Configuración de descarga con yt-dlp
    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": "%(title)s.%(ext)s",
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }
        ],
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"ytsearch:{query}", download=True)
            video_title = info["entries"][0]["title"]
            audio_filename = f"{video_title}.mp3"  # Nombre final del archivo MP3

        # Asegurar que el archivo existe antes de enviarlo
        if os.path.exists(audio_filename):
            with open(audio_filename, "rb") as audio:
                bot.send_audio(chat_id, audio, caption=f"🎵 Aquí tienes: {video_title}")
            
            os.remove(audio_filename)  # Eliminar el archivo después de enviarlo

        else:
            bot.send_message(chat_id, "❌ Error: No se pudo encontrar el archivo descargado")

    except Exception as e:
        bot.send_message(chat_id, f"❌ Ocurrió un error: {e}")
        

# Comando /video para descargar un video
import yt_dlp
@bot.message_handler(commands=["video"])
@acceso_restringido
def cmd_video(message):
    chat_id = message.chat.id
    args = message.text.split(maxsplit=1)

    if len(args) < 2:
        bot.send_message(chat_id, "Uso: /video nombre_del_video_o_URL")
        return

    video_name = args[1]
    bot.send_message(chat_id, f"🔍 Buscando el video: {video_name}...")

    # Buscar el video en YouTube usando Google Custom Search
    video_url = buscar_youtube(video_name)

    if not video_url:
        bot.send_message(chat_id, "❌ No se encontró el video.")
        return

    bot.send_message(chat_id, "🎥 Descargando video, espera un momento...")

    # Configuración de descarga con yt-dlp
    ydl_opts = {
        "format": "bestvideo+bestaudio/best",
        "outtmpl": "%(title)s.%(ext)s",  # Guarda el video con el nombre de la búsqueda
        "merge_output_format": "mp4", 
        "quiet": True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=True)
            video_title = info.get("title", video_name)
            video_file = f"{video_title}.mp4"

        # Verificar si el archivo existe antes de enviarlo
        if os.path.exists(video_file):
            with open(video_file, "rb") as video:
                bot.send_video(chat_id, video, caption=f"🎥 {video_title}")
            os.remove(video_file)  # Borrar después de enviarlo
        else:
            bot.send_message(chat_id, "❌ Error: No se encontró el archivo descargado.")

    except Exception as e:
        bot.send_message(chat_id, f"❌ Ocurrió un error: {e}")


# Función para buscar en Google con Custom Search A
def buscar_en_google(query):
    try:
        params = {
            "q": query,
            "cx": SEARCH_ENGINE_ID,
            "key": API_KEY
        }
        response = requests.get(SEARCH_URL, params=params)
        results = response.json()
        
        if "items" in results:
            enlaces = "\n".join([f"🔹 {item['title']}: {item['link']}" for item in results["items"][:5]])
            return enlaces
        else:
            return "No se encontraron resultados para la búsqueda."
    except Exception as e:
        print(f"Error en la búsqueda: {e}")
        return "Hubo un error al realizar la búsqueda."

# Comando /aibuscar
@bot.message_handler(commands=["aibuscar"])
@acceso_restringido
def cmd_aibuscar(message):
    query = message.text.replace("/aibuscar", "").strip()
    
    if not query:
        bot.reply_to(message, "❌ Debes escribir un texto después de /aibuscar")
        return

    bot.send_message(message.chat.id, f"🔍 Buscando en Google: {query} ...")

    resultado = buscar_en_google(query)
    bot.send_message(message.chat.id, resultado)
    
    
# Comando /aisticker
@bot.message_handler(commands=["aisticker"])
@acceso_restringido
def cmd_aisticker(message):
    chat_id = message.chat.id
    esperando_imagen[chat_id] = True  # Guardamos que el usuario espera enviar una imagen
    bot.send_message(chat_id, "Envíame una imagen y la convertiré en un sticker.")

# Manejar imágenes enviadas
@bot.message_handler(content_types=["photo"])
def recibir_imagen(message):
    chat_id = message.chat.id

    if chat_id in esperando_imagen and esperando_imagen[chat_id]:
        esperando_imagen[chat_id] = False  # Resetear estado

        # Obtener la mejor calidad de imagen disponible
        file_id = message.photo[-1].file_id
        file_info = bot.get_file(file_id)
        downloaded_file = bot.download_file(file_info.file_path)

        # Guardar la imagen temporalmente
        image_path = f"temp_{chat_id}.jpg"
        with open(image_path, "wb") as f:
            f.write(downloaded_file)

        # Convertir a sticker
        sticker_path = convertir_a_sticker(image_path)

        if sticker_path:
            bot.send_sticker(chat_id, open(sticker_path, "rb"))
            os.remove(sticker_path)  # Eliminar archivo después de enviarlo
        else:
            bot.send_message(chat_id, "❌ Ocurrió un error al crear el sticker")

        os.remove(image_path)  # Eliminar la imagen original
    else:
        bot.send_message(chat_id, "Envíame primero el comando /aisticker para crear un sticker.")

# Función para convertir una imagen en un sticker
def convertir_a_sticker(image_path):
    try:
        with Image.open(image_path) as img:
            img = img.convert("RGBA")  # Asegurar transparencia
            img.thumbnail((512, 512))  # Redimensionar a 512x512

            # Guardar como WebP
            sticker_path = image_path.replace(".jpg", ".webp")
            img.save(sticker_path, "WEBP", quality=100)

            return sticker_path
    except Exception as e:
        print(f"Error al convertir a sticker: {e}")
        return None           

# Respuestas automáticas a ciertas palabras clave
@bot.message_handler(func=lambda message: message.text.lower() in ["hola", "Hola", "gracias", "Gracias", "adiós", "Adiós"])
def respuestas_automaticas(message):
    texto = message.text.lower()
    respuestas = {
        "hola": "¡Hola! soy SicarioBot🤖, tu asistente virtual. ¿En qué te puedo ayudar? Ejecuta /menu para ver los comandos.",
        "Hola": "¡Hola! soy SicarioBot🤖, tu asistente virtual. ¿En qué te puedo ayudar? Ejecuta /menu para ver los comandos.",
        "gracias": "¡De nada! Siempre estoy aqui para ayudar. 😊",
        "Gracias": "¡De nada! Siempre estoy aqui para ayudar. 😊",
        "adiós": "¡Hasta luego! Que tengas un gran día. 👋",
        "Adiós": "¡Hasta luego! Que tengas un gran día. 👋"
    }
    bot.reply_to(message, respuestas[texto])

    
# Inicializar el bot
if __name__ == '__main__':
    try:
        print('SicarioBot iniciado..')
        bot.infinity_polling()
    except KeyboardInterrupt:
        print('\nSicarioBot detenido manualmente.')
    except Exception as e:
        print(f'Error inesperado: {e}')
    finally:
        print('SicarioBot finalizado..')