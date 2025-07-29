import os
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)
from datetime import datetime

TOKEN = "Token"
STATION_FILE = 'rwby.txt'


def get_current_station(chat_id):
    try:
        with open(STATION_FILE, 'r', encoding='utf-8') as f:
            for line in f:
                if line.startswith(f"{chat_id}:"):
                    return line.split(':', 1)[1].strip()
        return "Станция не указана"
    except FileNotFoundError:
        return "Станция не указана"


def save_station(chat_id, station):
    stations = {}
    try:
        with open(STATION_FILE, 'r', encoding='utf-8') as f:
            for line in f:
                if ':' in line:
                    cid, st = line.split(':', 1)
                    stations[cid] = st.strip()
    except FileNotFoundError:
        pass

    stations[str(chat_id)] = station
    with open(STATION_FILE, 'w', encoding='utf-8') as f:
        for cid, st in stations.items():
            f.write(f"{cid}:{st}\n")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [['Указать станцию'], ['Табло прибытия'], ['Табло отправления']]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text(
        "🚂 ЖД-бот: выберите действие",
        reply_markup=reply_markup
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    chat_id = update.message.chat_id

    if text == 'Указать станцию':
        await update.message.reply_text("📝 Введите название станции:")
        context.user_data['awaiting_station'] = True

    elif text == 'Табло прибытия':
        station = get_current_station(chat_id)
        time_now = datetime.now().strftime("%H:%M")
        response = (
                f"🛤️ Табло прибытия ({station})\n"
                f"🕒 Актуально на {time_now}\n\n"
                "<code>"
                "Поезд".ljust(20) + "Время".ljust(15) + "\n"
                                                        "-" * 35 + "\n"
                                                                   "Москва → Минск".ljust(20) + "14:00".ljust(15) + "\n"
                                                                                                                    "</code>"
        )
        await update.message.reply_text(response, parse_mode='HTML')

    elif text == 'Табло отправления':
        station = get_current_station(chat_id)
        time_now = datetime.now().strftime("%H:%M")
        response = (
                f"🚉 Табло отправления ({station})\n"
                f"🕒 Актуально на {time_now}\n\n"
                "<code>"
                "Поезд".ljust(20) + "Время".ljust(15) + "\n"
                                                        "-" * 35 + "\n"
                                                                   "Минск → Москва".ljust(20) + "19:00".ljust(15) + "\n"
                                                                                                                    "</code>"
        )
        await update.message.reply_text(response, parse_mode='HTML')

    elif context.user_data.get('awaiting_station'):
        save_station(chat_id, text)
        context.user_data['awaiting_station'] = False
        await update.message.reply_text(f"✅ Станция сохранена: {text}")


async def post_init(application):
    print("Бот успешно запущен")


def main():
    application = Application.builder().token(TOKEN).post_init(post_init).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("🔄 Запуск бота...")
    application.run_polling()


if __name__ == '__main__':
    if not os.path.exists(STATION_FILE):
        with open(STATION_FILE, 'w', encoding='utf-8'): pass
    main()
