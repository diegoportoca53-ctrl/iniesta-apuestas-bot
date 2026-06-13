import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler, ContextTypes
)
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime
import pytz

# ─── CONFIGURACIÓN ────────────────────────────────────────────────────────────
TOKEN = "8936540064:AAHx_mRYoXIQgIdsNltIKgUUs2wgFvVx-ME"          # 👈 Reemplaza con tu token
CANAL_ID = "iniestapuestas_bot"       # 👈 Reemplaza con el @usuario de tu canal

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
ZONA_HORARIA = pytz.timezone("America/Bogota")  # Cambia si estás en otro país

# ─── PRONÓSTICOS DEL DÍA (edítalos cada día) ──────────────────────────────────
PRONOSTICOS = [
    {
        "partido": "Real Madrid vs Barcelona",
        "liga": "🇪🇸 La Liga",
        "hora": "20:00",
        "prediccion": "1X (Real Madrid gana o empate)",
        "cuota": "1.65",
        "confianza": "⭐⭐⭐⭐",
        "analisis": "Real Madrid lleva 5 partidos sin perder en casa. Barcelona viaja con bajas importantes en defensa."
    },
    {
        "partido": "Manchester City vs Arsenal",
        "liga": "🏴󠁧󠁢󠁥󠁮󠁧󠁿 Premier League",
        "hora": "17:30",
        "prediccion": "Más de 2.5 goles",
        "cuota": "1.80",
        "confianza": "⭐⭐⭐⭐⭐",
        "analisis": "Los últimos 6 enfrentamientos entre estos equipos han terminado con más de 2 goles."
    },
]

# ─── PARTIDOS EN VIVO (actualiza manualmente o conecta una API de deportes) ───
PARTIDOS_VIVO = [
    {"partido": "PSG vs Lyon", "marcador": "2 - 1", "minuto": "67'", "liga": "🇫🇷 Ligue 1"},
    {"partido": "Juventus vs Inter", "marcador": "0 - 0", "minuto": "45'", "liga": "🇮🇹 Serie A"},
]

# ─── ESTADÍSTICAS GENERALES ───────────────────────────────────────────────────
ESTADISTICAS = {
    "total": 120,
    "ganados": 78,
    "perdidos": 32,
    "empates": 10,
    "racha": "5 aciertos seguidos 🔥",
    "mes": "Enero 2025",
}


# ─── FUNCIONES DE FORMATO ─────────────────────────────────────────────────────
def formato_pronostico(p, numero=1):
    return (
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"🎯 *PRONÓSTICO #{numero}*\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"⚽ *{p['partido']}*\n"
        f"{p['liga']} | 🕐 {p['hora']}\n\n"
        f"📌 *Predicción:* {p['prediccion']}\n"
        f"💰 *Cuota:* {p['cuota']}\n"
        f"🔥 *Confianza:* {p['confianza']}\n\n"
        f"📊 *Análisis:*\n_{p['analisis']}_\n"
        f"━━━━━━━━━━━━━━━━━━━━━━"
    )


def formato_vivo(p):
    return (
        f"🔴 *EN VIVO* | {p['liga']}\n"
        f"⚽ {p['partido']}\n"
        f"📊 Marcador: *{p['marcador']}* | {p['minuto']}\n"
    )


# ─── COMANDOS ─────────────────────────────────────────────────────────────────
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    teclado = [
        [InlineKeyboardButton("🎯 Pronósticos", callback_data="pronosticos")],
        [InlineKeyboardButton("🔴 En Vivo", callback_data="envivo"),
         InlineKeyboardButton("📊 Estadísticas", callback_data="estadisticas")],
        [InlineKeyboardButton("📢 Ir al Canal", url=f"https://t.me/{CANAL_ID.replace('@', '')}")],
    ]
    markup = InlineKeyboardMarkup(teclado)
    await update.message.reply_text(
        "🏆 *Bienvenido al Bot de Apuestas Pro*\n\n"
        "Selecciona una opción:",
        parse_mode="Markdown",
        reply_markup=markup
    )


async def cmd_pronostico(update: Update, context: ContextTypes.DEFAULT_TYPE):
    for i, p in enumerate(PRONOSTICOS, 1):
        await update.message.reply_text(
            formato_pronostico(p, i),
            parse_mode="Markdown"
        )


async def cmd_vivo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not PARTIDOS_VIVO:
        await update.message.reply_text("⏳ No hay partidos en vivo ahora mismo.")
        return
    texto = "🔴 *PARTIDOS EN VIVO*\n━━━━━━━━━━━━━━━━━━━━━━\n\n"
    for p in PARTIDOS_VIVO:
        texto += formato_vivo(p) + "\n"
    await update.message.reply_text(texto, parse_mode="Markdown")


async def cmd_estadisticas(update: Update, context: ContextTypes.DEFAULT_TYPE):
    e = ESTADISTICAS
    porcentaje = round((e["ganados"] / e["total"]) * 100, 1)
    texto = (
        f"📊 *ESTADÍSTICAS — {e['mes']}*\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"✅ Ganados: {e['ganados']}\n"
        f"❌ Perdidos: {e['perdidos']}\n"
        f"➖ Empates: {e['empates']}\n"
        f"📈 Total: {e['total']}\n"
        f"🎯 Efectividad: *{porcentaje}%*\n"
        f"🔥 Racha: {e['racha']}\n"
        f"━━━━━━━━━━━━━━━━━━━━━━"
    )
    await update.message.reply_text(texto, parse_mode="Markdown")


# ─── BOTONES INLINE ───────────────────────────────────────────────────────────
async def botones(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "pronosticos":
        for i, p in enumerate(PRONOSTICOS, 1):
            await query.message.reply_text(formato_pronostico(p, i), parse_mode="Markdown")

    elif query.data == "envivo":
        if not PARTIDOS_VIVO:
            await query.message.reply_text("⏳ No hay partidos en vivo ahora mismo.")
        else:
            texto = "🔴 *PARTIDOS EN VIVO*\n━━━━━━━━━━━━━━━━━━━━━━\n\n"
            for p in PARTIDOS_VIVO:
                texto += formato_vivo(p) + "\n"
            await query.message.reply_text(texto, parse_mode="Markdown")

    elif query.data == "estadisticas":
        e = ESTADISTICAS
        porcentaje = round((e["ganados"] / e["total"]) * 100, 1)
        texto = (
            f"📊 *ESTADÍSTICAS — {e['mes']}*\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"✅ Ganados: {e['ganados']}\n"
            f"❌ Perdidos: {e['perdidos']}\n"
            f"➖ Empates: {e['empates']}\n"
            f"📈 Total: {e['total']}\n"
            f"🎯 Efectividad: *{porcentaje}%*\n"
            f"🔥 Racha: {e['racha']}\n"
            f"━━━━━━━━━━━━━━━━━━━━━━"
        )
        await query.message.reply_text(texto, parse_mode="Markdown")


# ─── PUBLICACIÓN AUTOMÁTICA EN EL CANAL ───────────────────────────────────────
async def publicar_pronosticos(app):
    """Se ejecuta automáticamente cada día a las 9:00 AM"""
    texto = "🏆 *PRONÓSTICOS DEL DÍA* 🏆\n"
    texto += f"📅 {datetime.now(ZONA_HORARIA).strftime('%d/%m/%Y')}\n"
    texto += "━━━━━━━━━━━━━━━━━━━━━━\n\n"
    for i, p in enumerate(PRONOSTICOS, 1):
        texto += formato_pronostico(p, i) + "\n\n"
    texto += "⚠️ _Juega con responsabilidad. Solo apuesta lo que puedas perder._"
    await app.bot.send_message(chat_id=CANAL_ID, text=texto, parse_mode="Markdown")


async def publicar_recordatorio(app):
    """Recordatorio a las 6:00 PM"""
    await app.bot.send_message(
        chat_id=CANAL_ID,
        text=(
            "⏰ *RECORDATORIO DE PARTIDOS*\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n"
            "Los partidos de hoy están por comenzar.\n"
            "Revisa nuestros pronósticos del día 👆\n\n"
            "🤖 Usa /pronostico para verlos de nuevo."
        ),
        parse_mode="Markdown"
    )


# ─── MAIN ─────────────────────────────────────────────────────────────────────
def main():
    app = Application.builder().token(TOKEN).build()

    # Comandos
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("pronostico", cmd_pronostico))
    app.add_handler(CommandHandler("vivo", cmd_vivo))
    app.add_handler(CommandHandler("estadisticas", cmd_estadisticas))
    app.add_handler(CallbackQueryHandler(botones))

    # Programador de tareas automáticas
    scheduler = AsyncIOScheduler(timezone=ZONA_HORARIA)
    scheduler.add_job(publicar_pronosticos, "cron", hour=9, minute=0, args=[app])
    scheduler.add_job(publicar_recordatorio, "cron", hour=18, minute=0, args=[app])
    scheduler.start()

    logger.info("✅ Bot iniciado correctamente")
    app.run_polling()


if __name__ == "__main__":
    main()
