import os
from dotenv import load_dotenv

from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from app.commands import handle_get_flights_command, handle_get_flights_date_range_command

from app.serpapi.flights import get_flights_price

load_dotenv()
BOT_TOKEN = os.getenv("TELEGRAM_TOKEN")

async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f"Update {update} caused error {context.error}")

if __name__ == "__main__":
  app = Application.builder().token(BOT_TOKEN).build()
  app.add_handler(CommandHandler("flights", handle_get_flights_command))
  app.add_handler(CommandHandler("range", handle_get_flights_date_range_command))

  app.add_error_handler(error)
  app.run_polling(poll_interval=3)