import os
import re
import requests
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# Token del bot y URL del webhook
TOKEN = os.environ.get('BOT_TOKEN')
WEBHOOK_URL = os.environ.get('WEBHOOK_URL')

app = Application.builder().token(TOKEN).build()

# Parsear player_api.php
def parse_player_api(base_url, username, password):
    api_url = f"{base_url}/player_api.php?username={username}&password={password}"
    resp = requests.get(api_url).json()
    return resp

# Handler para /m3u
async def m3u_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text('Uso: /m3u <url_m3u>')
        return

    m3u_url = context.args[0]
    match = re.match(r"(https?://[^/]+)/get\.php\?username=([^&]+)&password=([^&]+)", m3u_url)
    if not match:
        await update.message.reply_text('Enlace inv¨¢lido')
        return

    base_url, username, password = match.groups()
    data = parse_player_api(base_url, username, password)

    panel = f"{base_url} | https://{base_url.split('://')[1]}"
    estado = "Active" if data.get('user_info', {}).get('status') == "Active" else "Inactive"
    conexiones = f"{data.get('user_info', {}).get('active_cons')}/{data.get('user_info', {}).get('max_connections')}"
    expiracion = data.get('user_info', {}).get('exp_date')
    zona = data.get('user_info', {}).get('timezone', 'Desconocida')
    mensaje = data.get('user_info', {}).get('message', 'Sin mensaje')
    live_count = data.get('user_info', {}).get('allowed_output_formats', [])
    categorias_live = len(data.get('categories', []))
    categorias_vod = len(data.get('vod_categories', []))
    categorias_series = len(data.get('series_categories', []))

    resp_text = (
        f"”9å3 *Panel:* {panel}\n"
        f"”9Ó4 *Usuario:* {username}\n"
        f"”9ä7 *Contrase0Š9a:* {password}\n"
        f"”9â0 *Estado:* {estado}\n"
        f"”9æ4 *Conexiones:* {conexiones}\n"
        f"77 *Expiraci¨®n:* {expiracion}\n"
        f"”9±1 *Zona:* {zona}\n"
        f"”9Ú6 *Mensaje:* {mensaje}\n"
        f"”9â4 *Live:* {categorias_live} | ”9Á0 *VOD:* {categorias_vod} | ”9ß2 *Series:* {categorias_series}\n"
        f"”9Ý0 *M3U Plus:* {m3u_url}\n"
        f"”9å3 *API:* {base_url}/player_api.php?username={username}&password={password}"
    )
    await update.message.reply_text(resp_text, parse_mode='Markdown', disable_web_page_preview=True)

# A0Š9adir handler
app.add_handler(CommandHandler('m3u', m3u_command))

# Flask app para el webhook
flask_app = Flask(__name__)

@flask_app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json(force=True)
    update = Update.de_json(data, app.bot)
    app.update_queue.put_nowait(update)
    return 'ok', 200

if __name__ == "__main__":
    app.bot.set_webhook(WEBHOOK_URL + "/webhook")
    flask_app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
