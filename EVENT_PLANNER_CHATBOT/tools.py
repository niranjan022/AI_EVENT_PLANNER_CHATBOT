import os
import random
from datetime import datetime, timedelta
from typing import List, Optional

import requests

from models import Event

TICKETMASTER_API_KEY = os.getenv("TICKETMASTER_API_KEY")

class TravelTools:
    def fetch_events(self, location: str, date: Optional[str] = None) -> List[Event]:
        """Fetch events from Ticketmaster; if unavailable or empty, return an empty list (no mock data)."""
        print(f"📡 TOOL: Fetching events for {location} on {date or 'unspecified'}...")

        if not TICKETMASTER_API_KEY:
            print("⚠️ TOOL: Missing TICKETMASTER_API_KEY; returning no events.")
            return []

        live = self._fetch_ticketmaster(location, date)
        if live:
            return live

        print("ℹ️ TOOL: No events returned from Ticketmaster.")
        return []

    def _fetch_ticketmaster(self, location: str, date: Optional[str]) -> List[Event]:
        base_url = "https://app.ticketmaster.com/discovery/v2/events.json"

        # Build date window
        try:
            day = datetime.fromisoformat(date) if date else datetime.utcnow().date()
        except ValueError:
            day = datetime.utcnow().date()
        start_dt = datetime.combine(day, datetime.min.time())
        end_dt = start_dt + timedelta(days=1) - timedelta(seconds=1)

        params = {
            "apikey": TICKETMASTER_API_KEY,
            "keyword": location,
            "startDateTime": start_dt.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "endDateTime": end_dt.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "size": 20,
            "sort": "relevance,desc",
            "locale": "*",
        }

        try:
            resp = requests.get(base_url, params=params, timeout=10)
            resp.raise_for_status()
            data = resp.json()
        except Exception as e:
            print(f"⚠️ TOOL: Ticketmaster error: {e}")
            return []

        events = data.get("_embedded", {}).get("events", [])
        results = []
        for idx, ev in enumerate(events):
            name = ev.get("name", "Event")
            classifications = ev.get("classifications", [])
            tags = []
            if classifications:
                c0 = classifications[0]
                for key in ("segment", "genre", "subGenre"):
                    obj = c0.get(key) or {}
                    if obj.get("name"):
                        tags.append(obj["name"].lower())

            venue = ev.get("_embedded", {}).get("venues", [{}])[0]
            venue_name = venue.get("name") or venue.get("city", {}).get("name") or "Venue"
            address_parts = [
                venue.get("address", {}).get("line1"),
                venue.get("city", {}).get("name"),
                venue.get("state", {}).get("name") or venue.get("state", {}).get("stateCode"),
                venue.get("country", {}).get("countryCode"),
            ]
            address = ", ".join([p for p in address_parts if p]) or None

            price_ranges = ev.get("priceRanges", [])
            cost = 0
            if price_ranges:
                cost = int(price_ranges[0].get("min", 0))

            rating = ev.get("promoter", {}).get("id")
            try:
                rating = float(ev.get("popularity", 0)) / 10.0
            except Exception:
                rating = 4.0 + (idx % 5) * 0.1

            results.append(Event(
                id=idx + 1,
                name=name,
                category=tags[0] if tags else "Event",
                tags=tags or ["event"],
                rating=round(rating, 2),
                duration_mins=90,
                cost=cost,
                location=venue_name,
                address=address,
            ))

        return results

    def get_travel_time(self, loc_a: str, loc_b: str) -> int:
        """MOCK API: Simulates Google Distance Matrix."""
        # Simple logic: if locations are different, take 30 mins.
        if loc_a == loc_b: return 0
        return 30