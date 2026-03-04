from typing import List, Optional
from pydantic import BaseModel, Field

class UserRequest(BaseModel):
    """Parsed user intent."""
    location: str
    date: str
    preferences: List[str] = Field(description="List of user interests e.g. ['jazz', 'quiet']")
    start_time: str = Field(description="Start time in HH:MM 24hr format. Use '09:00' if not specified.")
    end_time: str = Field(description="End time in HH:MM 24hr format. Use '22:00' if not specified.")

class Event(BaseModel):
    """A single event object."""
    id: int
    name: str
    category: str
    tags: List[str]
    rating: float
    duration_mins: int
    cost: int
    location: str
    address: Optional[str] = None
    score: Optional[float] = 0.0

class ItineraryItem(BaseModel):
    """A scheduled item in the final plan."""
    time_slot: str
    activity: str
    location: str
    notes: str


class SavedItinerary(BaseModel):
    """User-saved itinerary metadata plus items."""
    id: str
    title: str
    prompt: str
    date: str
    location: str
    items: List[ItineraryItem]
    created_at: str


class ChatMessage(BaseModel):
    """History of chat exchanges for a user."""
    role: str
    content: str
    timestamp: str


class UserProfile(BaseModel):
    """Minimal in-app user record (not production-ready auth)."""
    id: str
    email: str
    name: str
    saved_itineraries: List[SavedItinerary] = Field(default_factory=list)
    chat_history: List[ChatMessage] = Field(default_factory=list)