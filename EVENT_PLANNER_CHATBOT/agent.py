import os
import json
import re
from datetime import datetime, timedelta
from typing import List, Dict, Optional

from openai import OpenAI, APIStatusError
from dotenv import load_dotenv
from models import UserRequest, ItineraryItem
from tools import TravelTools
from ranking_engine import RankingEngine

load_dotenv()
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "gemini").lower()
GROK_MODEL = os.getenv("GROK_MODEL", "grok-2-mini")
GROK_API_KEY = os.getenv("GROK_API_KEY")
GROK_API_BASE = os.getenv("GROK_API_BASE", "https://api.x.ai/v1")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_API_BASE = os.getenv("GROQ_API_BASE", "https://api.groq.com/openai/v1")

class TravelAgent:
    def __init__(self):
        self.provider = LLM_PROVIDER
        if self.provider == "grok":
            if not GROK_API_KEY:
                raise RuntimeError("GROK_API_KEY is required when LLM_PROVIDER=grok")
            self.client = OpenAI(api_key=GROK_API_KEY, base_url=GROK_API_BASE)
            self.model = GROK_MODEL
        elif self.provider == "groq":
            if not GROQ_API_KEY:
                raise RuntimeError("GROQ_API_KEY is required when LLM_PROVIDER=groq")
            self.client = OpenAI(api_key=GROQ_API_KEY, base_url=GROQ_API_BASE)
            self.model = GROQ_MODEL
        self.tools = TravelTools()
        self.ranker = RankingEngine()

    def _generate_text(self, prompt: str) -> str:
        """Return free-form text from the selected LLM provider."""
        if self.provider in {"grok", "groq"}:
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a concise travel assistant."},
                    {"role": "user", "content": prompt},
                ],
            )
            return completion.choices[0].message.content

        response = self.model.generate_content(prompt)
        return response.text

    def _generate_json(self, prompt: str) -> str:
        """Call the selected LLM and return raw JSON text."""
        if self.provider == "grok":
            try:
                completion = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "You are a concise travel assistant. Return strict JSON only."},
                        {"role": "user", "content": prompt},
                    ],
                    response_format={"type": "json_object"},
                )
                return completion.choices[0].message.content
            except Exception as e:
                msg = str(e)
                if "Model not found" in msg or "model" in msg.lower():
                    raise RuntimeError(
                        f"Grok model '{self.model}' not available. Set GROK_MODEL to one of: grok-2, grok-2-mini, grok-vision-beta."
                    ) from e
                raise

        if self.provider == "groq":
            try:
                completion = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "You are a concise travel assistant. Return strict JSON only."},
                        {"role": "user", "content": prompt},
                    ],
                    response_format={"type": "json_object"},
                )
                return completion.choices[0].message.content
            except Exception as e:
                msg = str(e)
                if "model" in msg.lower():
                    raise RuntimeError(
                        f"Groq model '{self.model}' not available. Set GROQ_MODEL to one of: llama-3.3-70b-versatile, llama-3.1-70b-versatile, mixtral-8x7b-32768."
                    ) from e
                raise

        response = self.model.generate_content(
            prompt,
            generation_config={"response_mime_type": "application/json"}
        )
        return response.text

    def parse_request(self, user_input: str) -> UserRequest:
        """Uses LLM to convert chat text into structured JSON."""
        prompt = f"""
        Extract travel details from this text into JSON.
        If times are not specified, assume 09:00 to 22:00.
        Input: "{user_input}"
        """
        parsed = json.loads(self._generate_json(prompt))
        # Normalize common model output variants
        prefs = parsed.get("preferences") or parsed.get("interests") or []
        if isinstance(prefs, str):
            prefs = [prefs]
        if isinstance(prefs, dict):
            prefs = list(prefs.values())

        normalized = {
            "location": (parsed.get("location") or parsed.get("destination") or "").strip(),
            "date": (parsed.get("date") or parsed.get("day") or parsed.get("travelDate") or "").strip(),
            "preferences": prefs,
            "start_time": (parsed.get("start_time") or parsed.get("startTime") or parsed.get("start") or "09:00").strip(),
            "end_time": (parsed.get("end_time") or parsed.get("endTime") or parsed.get("end") or "22:00").strip(),
        }
        return UserRequest(**normalized)

    def generate_itinerary(
        self,
        user_input: str,
        *,
        location: Optional[str] = None,
        date: Optional[str] = None,
        preferences: Optional[List[str]] = None,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
    ):
        # 1. Understand User
        if location and date:
            req = UserRequest(
                location=location.strip(),
                date=date.strip(),
                preferences=preferences or [],
                start_time=(start_time or "09:00").strip(),
                end_time=(end_time or "22:00").strip(),
            )
        else:
            req = self.parse_request(user_input)

        self._validate_request(req)
        # print(f"✅ AGENT: Parsed Request -> {req.location}, Likes: {req.preferences}")

        # 2. Fetch External Data
        event_date = self._resolve_date(req.date)
        raw_events = self.tools.fetch_events(req.location, event_date)
        if not raw_events:
            return []

        # 3. Apply Logic (Ranking)
        # Filter top 4 events to fit in a day
        sorted_events = self.ranker.rank_events(req.preferences, raw_events)[:4]
        # print(f"✅ AGENT: Selected top {len(sorted_events)} events: {[e.name for e in sorted_events]}")

        # 4. Generate Final Plan using LLM
        # We pass the *structured* data to Gemini so it just formats, doesn't hallucinate.
        enriched = []
        for e in sorted_events:
            d = e.model_dump()
            addr = d.get("address")
            if addr:
                d["location_display"] = f"{d.get('location')} — {addr}"
            else:
                d["location_display"] = d.get("location")
            enriched.append(d)
        context_data = json.dumps(enriched)
        
        final_prompt = f"""
        You are an expert travel planner.
        Create a chronological itinerary for {req.date} in {req.location}.
        
        Constraints:
        - Start at {req.start_time}.
        - Use ONLY these events: {context_data}.
        - Arrange them logically.
        - Add 30 mins travel time between events.
        
        Output Format:
        Return a JSON list of objects with keys: time_slot, activity, location, notes.
        - Use the provided 'location_display' string for the location field so users see the destination/venue.
        Make the 'notes' field persuasive and exciting based on the user's likes: {req.preferences}.
        """
        final_raw = json.loads(self._generate_json(final_prompt))

        # Normalize various JSON response shapes into a list of itinerary items
        if isinstance(final_raw, dict):
            if "itinerary" in final_raw:
                items = final_raw["itinerary"]
            elif "plan" in final_raw:
                items = final_raw["plan"]
            elif "items" in final_raw:
                items = final_raw["items"]
            else:
                items = [final_raw]
        elif isinstance(final_raw, list):
            items = final_raw
        else:
            raise ValueError("Unexpected itinerary format from LLM")

        return items

    def answer_question(self, itinerary: List[Dict], question: str) -> str:
        """Allow follow-up questions grounded in a specific itinerary."""
        if not itinerary:
            raise ValueError("Itinerary is required to answer follow-up questions.")
        context = json.dumps(itinerary)
        prompt = f"""
You are a professional AI travel assistant.

Guidelines:
- Use the itinerary as primary context.
- You may use accurate general knowledge if helpful.
- Never fabricate itinerary details.
- Do not restate the question.
- Do not mention "itinerary JSON" or explain your reasoning.
- Avoid meta commentary.
- Be clear, natural, and conversational.
- Keep responses concise but helpful.
- Ensure suggestions match the event timing realistically (e.g., suggest lunch instead of dinner if events are in the morning).
- Avoid overly specific location recommendations unless necessary.

Formatting Rules (Strictly Follow):
- Format responses using clean Markdown.
- Use "-" (dash) for bullet points, not "*".
- Always add a blank line before starting a bullet list.
- Do NOT merge bullet points into a paragraph.
- Keep lists short and readable.
- Use bold (**text**) only for important names like venues or locations.
- Do not overuse bold formatting.
- Maintain proper spacing between sections.

Itinerary:
{context}

User Question:
{question}

Answer:
"""
        return self._generate_text(prompt)

    def _resolve_date(self, date_str: str) -> str:
        """Normalize date strings like 'today'/'tomorrow' to YYYY-MM-DD, else require valid ISO date."""
        if not date_str:
            raise ValueError("Date is required.")

        today = datetime.utcnow().date()
        lower = date_str.strip().lower()
        if "tomorrow" in lower:
            target = today + timedelta(days=1)
        elif "today" in lower:
            target = today
        else:
            try:
                target = datetime.fromisoformat(date_str).date()
            except ValueError:
                raise ValueError("Use a valid date in YYYY-MM-DD.")

        if target < today:
            raise ValueError("Pick a date from today onward.")

        return target.isoformat()

    def _validate_request(self, req: UserRequest) -> None:
        """Strict validation for location and date-related fields."""
        if not req.location or not req.location.strip():
            raise ValueError("Location is required.")
        if re.search(r"[^\w\s,.-]", req.location):
            raise ValueError("Use letters, numbers, spaces, commas, or hyphens only for location.")