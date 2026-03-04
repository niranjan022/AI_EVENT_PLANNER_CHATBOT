from typing import List
from models import Event

class RankingEngine:
    def rank_events(self, user_prefs: List[str], events: List[Event]) -> List[Event]:
        """
        Scores events based on overlap between user_prefs and event tags.
        Score = (Tag Matches * 2) + (Rating / 2)
        """
        print(f"🧠 ENGINE: Ranking {len(events)} events for preferences: {user_prefs}")
        
        ranked_events = []
        user_prefs_lower = [p.lower() for p in user_prefs]

        for event in events:
            # 1. Calculate Keyword Match Score
            match_count = sum(1 for tag in event.tags if tag in user_prefs_lower)
            
            # 2. Weighted Formula
            # Matches are worth 2.0 points, Rating is added as a bonus (0-2.5 pts)
            score = (match_count * 2.0) + (event.rating / 2.0)
            
            # Penalize slightly if it doesn't match ANY preference
            if match_count == 0:
                score = score * 0.5

            event.score = round(score, 2)
            ranked_events.append(event)

        # Sort strictly by score (Descending)
        return sorted(ranked_events, key=lambda x: x.score, reverse=True)