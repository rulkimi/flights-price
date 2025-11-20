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
  "api_key": SERPAPI_API_KEY
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
  best_flights = results["best_flights"]
  return best_flights