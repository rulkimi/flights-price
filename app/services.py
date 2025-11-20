def human_readable_duration(minutes: int) -> str:
  hours = minutes // 60
  mins = minutes % 60
  return f"{hours}h {mins}m" if hours else f"{mins}m"


def format_price(price) -> str:
  try:
    price_int = int(price)
    return f"RM {price_int:,}"
  except (ValueError, TypeError):
    return "N/A"


def parse_flights(best_flights: list) -> list:
  parsed = []

  for option in best_flights:
    flights = option.get("flights", [])
    if not flights or not isinstance(flights, list):
      continue

    airline_names = {seg.get("airline", "Unknown Airline") for seg in flights}
    flight_numbers = {seg.get("flight_number") for seg in flights if seg.get("flight_number")}

    booking = option.get("booking_url")
    if not booking:
      dep = flights[0].get("departure_airport", {}).get("id", "")
      arr = flights[-1].get("arrival_airport", {}).get("id", "")
      booking = f"https://www.google.com/search?q=flights+from+{dep}+to+{arr}"

    parsed.append({
      "airlines": "/".join(airline_names),
      "flight_numbers": ", ".join(flight_numbers) if flight_numbers else "N/A",
      "price": format_price(option.get("price")),
      "currency": "MYR",
      "duration": human_readable_duration(option.get("total_duration", 0)),
      "link": booking,
    })

  return parsed
