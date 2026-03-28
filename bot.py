import telebot
import time
import random
from openai import OpenAI
import threading
from datetime import datetime
import os
TOKEN = os.getenv("8620327068:AAFT4nnwTmntE_-2Gwb1oRBJcIhDOu9fQlg")

bot = telebot.TeleBot(TOKEN)

usuarios = set()

client = OpenAI(
    api_key=os.getenv("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"),
    base_url="https://openrouter.ai/api/v1"
)

memoria = {}
nombres = {}
datos_usuario = {}

def obtener_historial(user_id):
    if user_id not in memoria:
        memoria[user_id] = [
            {
                "role": "system",
                "content": (
    "Eres como un hermano mayor cercano. "
    "Hablas como mexicano normal. "
    "Respondes SIEMPRE corto (máximo 1 o 2 frases). "
    "No das explicaciones largas. "
    "No repites lo que dice el usuario. "
    "No resumes mensajes. "
    "Hablas natural como conversación real. "
    "A veces respondes muy corto como: 'arre', 'sí', 'jajaja'. "
    "A veces haces preguntas simples para seguir la plática. "
    "No hablas como robot ni dices que eres IA."
)
            }
        ]
    return memoria[user_id]

@bot.message_handler(func=lambda message: True)
def responder(message):
    usuarios.add(message.chat.id)

    user_id = message.from_user.id
    historial = obtener_historial(user_id)

    texto_usuario = message.text.lower()

    # 🧠 guardar datos
    if user_id not in datos_usuario:
        datos_usuario[user_id] = []

    if "me gusta" in texto_usuario:
        datos_usuario[user_id].append(message.text)

    if "tengo" in texto_usuario and "años" in texto_usuario:
        datos_usuario[user_id].append(message.text)

    if "soy de" in texto_usuario or "vivo en" in texto_usuario:
        datos_usuario[user_id].append(message.text)

    # 🧠 guardar nombre
    if "me llamo" in texto_usuario:
        nombre = message.text.split("me llamo")[-1].strip()
        nombres[user_id] = nombre

    # 🧠 usar memoria
    if user_id in datos_usuario and len(datos_usuario[user_id]) > 0:
        info = ". ".join(datos_usuario[user_id][-3:])
        historial.append({
            "role": "system",
            "content": f"Recuerda esto del usuario: {info}"
        })

    historial.append({"role": "user", "content": message.text})
historial.append({
    "role": "system",
    "content": "No repitas lo que dijo el usuario. Responde directo."
})

    bot.send_chat_action(message.chat.id, "typing")
    time.sleep(random.uniform(1, 5))

    try:
        respuesta = client.chat.completions.create(
            model="openrouter/auto",
            messages=historial,
            temperature=1.2
        )

        texto = respuesta.choices[0].message.content #
# cortar si está muy largo
if len(texto) > 120:
    texto = texto[:120]

        # usar nombre
        if user_id in nombres and random.random() < 0.5:
            texto = f"{nombres[user_id]}, {texto}"

        historial.append({"role": "assistant", "content": texto})

        bot.reply_to(message, texto)

    except Exception as e:
        print("ERROR:", e)
        bot.reply_to(message, "Jajaja se me fue el pedo 😅 intenta otra vez")

def escribir_solo():
    while True:
        if len(usuarios) > 0:
            user_id = random.choice(list(usuarios))

            hora = datetime.now().hour

            if 6 <= hora < 12:
                mensajes = [
                    "Buenos días bro 😎 ya despertaste?",
                    "Cómo amaneciste?",
                ]
            elif 12 <= hora < 19:
                mensajes = [
                    "Qué haces ahorita? 👀",
                    "Todo bien hoy o qué?",
                ]
            else:
                mensajes = [
                    "Ya te vas a dormir o qué 🌙",
                    "Sigues vivo o ya caíste 😂",
                ]

            mensaje = random.choice(mensajes)

            # usar nombre
            if user_id in nombres:
                mensaje = f"{nombres[user_id]}, {mensaje}"

            # usar info
            if user_id in datos_usuario and len(datos_usuario[user_id]) > 0:
                dato = random.choice(datos_usuario[user_id])
                mensaje += f" Oye, {dato} ¿no?"

            try:
                bot.send_chat_action(user_id, "typing")
                time.sleep(random.uniform(1, 3))
                bot.send_message(user_id, mensaje)
            except:
                pass

        time.sleep(random.uniform(300, 900))

threading.Thread(target=escribir_solo).start()

bot.polling()
