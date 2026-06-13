import logging
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime
import pytz

TOKEN = "8936540064:AAGCR1xRM6vREHX2kY5Z9JPWS6Gvo8F2ijc"
CANAL_ID = "@iniesta_apuestas"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
ZONA_HORARIA = pytz.timezone("America/Bogota")

PRONOSTICOS = [
    {
        "partido": "Real Madrid vs Barcelona",
        "liga": "La Liga",
        "hora": "20:00",
        "prediccion": "Real Madrid gana o empate",
        "cuota": "1.65",
        "confianza": "4/5",
        "analisis": "Real Madrid lleva 5 partidos sin perder en casa."
    },
    {
        "partido": "Manchester City vs Arsenal",
        "liga": "Premier League",
        "hora": "17:30",
        "prediccion": "Mas de 2.5 goles",
        "cuota": "1.80",
        "confianza": "5/5",
        "analisis": "Los ultimos 6 enfrentamientos tuvieron mas de 2 goles."
    },
]

PARTIDOS_VIVO = [
    {"partido": "PSG vs Lyon", "marcador": "2 - 1", "minuto": "67", "liga": "Ligue 1"},
    {"partido": "Juventus vs Inter", "marcador": "0 - 0", "minuto": "45", "liga": "Serie A"},
]

ESTADISTICAS = {
    "total": 120,
    "ganados": 78,
    "perdidos": 32,
    "empates": 10,
    "racha": "5 aciertos seguidos",
    "mes": "Junio 2025",
}


def formato_pronostico(p, numero=1):
    return (
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        f"PRONOSTICO #{numero}\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        f"Partido: {p['partido']}\n"
        f"Liga: {p['liga']} | Hora: {p['hora']}\n\n"
        f"Prediccion: {p['prediccion']}\n"
        f"Cuota: {p['cuota']}\n"
        f"Confianza: {p['confianza']}\n\n"
        f"Analisis:\n{p['analisis']}\n"
        "━━━━━━━━━━━━━━━━━━━━━━"
    )


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    teclado = [
        [InlineKeyboardButton("Pronosticos", callback_data="pronosticos")],
        [InlineKeyboardButton("En Vivo", callback_data="envivo"),
         InlineKeyboardButton("Estadisticas", callback_data="estadisticas")],
        [InlineKeyboardButton("Ir al Canal", url=f"https://t.me/{CANAL_ID.replace('@', '')}")],
    ]
    markup = InlineKeyboardMarkup(teclado)
    await update.message.reply_text(
        "Bienvenido al Bot de Iniesta Apuestas\n\nSelecciona una opcion:",
        reply_markup=markup
    )


async def cmd_pronostico(update: Update, context: ContextTypes.DEFAULT_TYPE):
    for i, p in enumerate(PRONOSTICOS, 1):
        await update.message.reply_text(formato_pronostico(p, i))


async def cmd_vivo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not PARTIDOS_VIVO:
        await update.message.reply_text("No hay partidos en vivo ahora mismo.")
        return
    texto = "PARTIDOS EN VIVO\n━━━━━━━━━━━━━━━━━━━━━━\n\n"
    for p in PARTIDOS_VIVO:
        texto += f"{p['liga']}\n{p['partido']}\nMarcador: {p['marcador']} | Min {p['minuto']}\n\n"
    await update.message.reply_text(texto)


async def cmd_estadisticas(update: Update, context: ContextTypes.DEFAULT_TYPE):
    e = ESTADISTICAS
    porcentaje = round((e["ganados"] / e["total"]) * 100, 1)
    texto = (
        f"ESTADISTICAS - {e['mes']}\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        f"Ganados: {e['ganados']}\n"
        f"Perdidos: {e['perdidos']}\n"
        f"Empates: {e['empates']}\n"
        f"Total: {e['total']}\n"
        f"Efectividad: {porcentaje}%\n"
        f"Racha: {e['racha']}\n"
        "━━━━━━━━━━━━━━━━━━━━━━"
    )
    await update.message.reply_text(texto)


async def botones(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "pronosticos":
        for i, p in enumerate(PRONOSTICOS, 1):
            await query.message.reply_text(formato_pronostico(p, i))
    elif query.data == "envivo":
        if not PARTIDOS_VIVO:
            await query.message.reply_text("No hay partidos en vivo ahora mismo.")
        else:
            texto = "PARTIDOS EN VIVO\n━━━━━━━━━━━━━━━━━━━━━━\n\n"
            for p in PARTIDOS_VIVO:
                texto += f"{p['liga']}\n{p['partido']}\nMarcador: {p['marcador']} | Min {p['minuto']}\n\n"
            await query.message.reply_text(texto)
    elif query.data == "estadisticas":
        e = ESTADISTICAS
        porcentaje = round((e["ganados"] / e["total"]) * 100, 1)
        texto = (
            f"ESTADISTICAS - {e['mes']}\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n"
            f"Ganados: {e['ganados']}\n"
            f"Perdidos: {e['perdidos']}\n"
            f"Empates: {e['empates']}\n"
            f"Total: {e['total']}\n"
            f"Efectividad: {porcentaje}%\n"
            f"Racha: {e['racha']}\n"
            "━━━━━━━━━━━━━━━━━━━━━━"
        )
        await query.message.reply_text(texto)


async def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("pronostico", cmd_pronostico))
    app.add_handler(CommandHandler("vivo", cmd_vivo))
    app.add_handler(CommandHandler("estadisticas", cmd_estadisticas))
    app.add_handler(CallbackQueryHandler(botones))

    scheduler = AsyncIOScheduler(timezone=ZONA_HORARIA)
    scheduler.start()

    logger.info("Bot iniciado correctamente")
    await app.run_polling()


if __name__ == "__main__":
    asyncio.run(main())
