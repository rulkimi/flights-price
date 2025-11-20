from telegram import Update
from telegram.ext import ContextTypes

from .serpapi.flights import get_flights_price
from .services import parse_flights

async def handle_get_flights_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
  try:
    raw_flights = get_flights_price()
    flights = parse_flights(raw_flights)

    if not flights:
      await update.message.reply_text("Sorry, I couldn't find any flights.")
      return

    # Build Telegram response
    lines = []
    for f in flights:
      line = (
        f"<b>Airline:</b> {f['airlines']}\n"
        f"<b>Flight numbers:</b> {f['flight_numbers']}\n"
        f"<b>Price:</b> {f['price']} {f['currency']}\n"
        f"<b>Total duration:</b> {f['duration']}\n"
        f'<b>See/Book:</b> <a href="{f["link"]}">Google Flights</a>'
      )
      lines.append(line)

    output = "Here are the best flights I found:\n\n" + "\n\n".join(lines)
    await update.message.reply_text(output, parse_mode="HTML", disable_web_page_preview=False)

  except Exception as e:
    print(f"Error in flights handler: {e}")
    await update.message.reply_text("An error occurred while retrieving flight information.")

async def handle_get_flights_date_range_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
  try:
    # Only consider 10 durations like 12-21, 13-22, ... 21-30
    res_lines = []
    for i in range(12, 22):
      outbound = f"2026-04-{str(i).zfill(2)}"
      ret = f"2026-04-{str(i+9).zfill(2)}"
      raw = get_flights_price(outbound_date=outbound, return_date=ret)
      parsed = parse_flights(raw)
      # Take one best result for each date span, if available
      if parsed:
        f = parsed[0]
        info = (
          f"<b><u>{outbound} - {ret}</u></b>\n"
          f"<b>Airline:</b> {f['airlines']}\n"
          f"<b>Flight numbers:</b> {f['flight_numbers']}\n"
          f"<b>Price:</b> {f['price']} {f['currency']}\n"
          f"<b>Duration:</b> {f['duration']}\n"
          f'<b>See/Book:</b> <a href="{f["link"]}">Google Flights</a>'
        )
        res_lines.append(info)

    if not res_lines:
      await update.message.reply_text("Sorry, could not find any flights for the range 12-21 to 21-30 April.")
      return

    full_out = "Best flights for these date ranges:\n\n" + "\n\n".join(res_lines)
    await update.message.reply_text(full_out, parse_mode="HTML", disable_web_page_preview=False)
  except Exception as ex:
    print(f"Error in date range flights handler: {ex}")
    await update.message.reply_text("An error occurred while looking for flights in date range.")

