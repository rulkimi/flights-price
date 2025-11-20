from telegram import Update
from telegram.ext import ContextTypes
from .serpapi.flights import get_flights_price
from .services import parse_flights
import re
from datetime import datetime, timedelta

async def handle_get_flights_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        raw_flights = get_flights_price()
        flights = parse_flights(raw_flights)

        if not flights:
            await update.message.reply_text("Sorry, I couldn't find any flights.")
            return

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
        text = update.message.text or ""
        date_pattern = r"(\d{4}-\d{2}-\d{2})\s*to\s*(\d{4}-\d{2}-\d{2})"
        match = re.search(date_pattern, text)
        if match:
            start_str, end_str = match.group(1), match.group(2)
        else:
            start_str = "2026-04-10"
            end_str = "2026-04-30"

        try:
            start_date = datetime.strptime(start_str, "%Y-%m-%d")
            end_date = datetime.strptime(end_str, "%Y-%m-%d")
        except ValueError:
            await update.message.reply_text(
                "Invalid date format. Use /range YYYY-MM-DD to YYYY-MM-DD (example: /range 2025-04-10 to 2025-04-30)"
            )
            return

        day_diff = (end_date - start_date).days
        if day_diff < 9:
            await update.message.reply_text("Date range must cover at least 10 days.")
            return

        res_lines = []
        for i in range(9):
            outbound_date = start_date + timedelta(days=i)
            return_date = outbound_date + timedelta(days=9)
            if return_date > end_date:
                break
            outbound_str = outbound_date.strftime("%Y-%m-%d")
            return_str = return_date.strftime("%Y-%m-%d")

            try:
                raw_and_link = get_flights_price(outbound_date=outbound_str, return_date=return_str)
                if isinstance(raw_and_link, tuple):
                    raw, prettify_html_file = raw_and_link
                else:
                    raw = raw_and_link
                    prettify_html_file = None
                if not isinstance(raw, list):
                    raw = []
            except Exception as e:
                print(f"Error fetching flights for {outbound_str} to {return_str}: {e}")
                raw = []
                prettify_html_file = None

            parsed = parse_flights(raw)
            if parsed:
                # List ALL available best flights, include airlines, price, duration, stops
                lines = []
                for idx, f in enumerate(parsed):
                    # Try to determine number of stops from the original raw data if possible
                    num_stops = None
                    if idx < len(raw):
                        flights = raw[idx].get("flights", [])
                        if isinstance(flights, list) and len(flights) > 0:
                            num_stops = len(flights) - 1
                    if num_stops is not None and num_stops >= 0:
                        stops_text = f"{num_stops} stop" if num_stops == 1 else f"{num_stops} stops"
                    else:
                        stops_text = "N/A stops"

                    lines.append(
                        f"- {f['airlines']}: {f['price']} {f['currency']} | {f['duration']} | {stops_text}"
                    )
                if lines:
                    if prettify_html_file:
                        flights_link = prettify_html_file
                        link_text = "View Google Flights result (SerpApi prettified)"
                    else:
                        flights_link = f"https://www.google.com/search?q=flights+from+KUL+to+destination+{outbound_str}+to+{return_str}"
                        link_text = "See on Google"
                    info = (
                        f"<b><u>{outbound_str} - {return_str}</u></b>\n"
                        + "\n".join(lines)
                        + "\n"
                        f'<b>Flight search:</b> <a href="{flights_link}">{link_text}</a>'
                    )
                    res_lines.append(info)

        if not res_lines:
            await update.message.reply_text(
                f"Sorry, could not find any flights for the range {start_str} to {end_str}."
            )
            return

        full_out = (
            f"Best flights (airlines, price, duration, stops) for these date ranges ({start_str} to {end_str}):\n\n"
            + "\n\n".join(res_lines)
        )
        await update.message.reply_text(
            full_out, parse_mode="HTML", disable_web_page_preview=False
        )
    except Exception as ex:
        print(f"Error in date range flights handler: {ex}")
        await update.message.reply_text(
            "An error occurred while looking for flights in date range."
        )
