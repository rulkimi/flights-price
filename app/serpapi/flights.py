import os
from serpapi import GoogleSearch
from dotenv import load_dotenv

load_dotenv()

SERPAPI_API_KEY = os.getenv("SERPAPI_API_KEY")

BASE_PARAMS = {
  "engine": "google_flights",
  "hl": "en",
  "gl": "my",
  "currency": "MYR",
  "api_key": SERPAPI_API_KEY,
  "include_airlines":"MH"
}

def get_flights_price(
  derpature_id: str = "KUL",
  arrival_id: str = "AKL",
  outbound_date: str = "2026-04-13",
  return_date: str = "2026-04-22"
):
  params = BASE_PARAMS.copy()
  params.update({
    "departure_id": derpature_id,
    "arrival_id": arrival_id,
    "outbound_date": outbound_date,
    "return_date": return_date
  })

  search = GoogleSearch(params)
  results = search.get_dict()
  print(results)
  best_flights = results.get("best_flights")
  if not best_flights:
    best_flights = results.get("other_flights", [])

  # Try to get prettify_html_file from search_metadata if available
  pretty_html_file = None
  search_metadata = results.get("search_metadata", {})
  if isinstance(search_metadata, dict):
    pretty_html_file = search_metadata.get("prettify_html_file")

  return best_flights, pretty_html_file