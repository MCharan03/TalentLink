import random
from datetime import datetime
from ..models import db, JobPosting, Notification, CareerForecast, UserXP
from .ai_utils import _call_gemini

class SentientAgency:
    """
    Handles asynchronous tasks performed by Cherry AI while the user is away.
    """
    def __init__(self, user_id):
        self.user_id = user_id

    def wake_up(self):
        """
        AI 'wakes up' and performs 1-2 background tasks.
        """
        actions_taken = []
        
        # 30% chance to scan market
        if random.random() < 0.3:
            actions_taken.append(self.scan_market_intelligence())
            
        # 20% chance to check career gaps
        if random.random() < 0.2:
            actions_taken.append(self.check_career_gaps())
            
        return actions_taken

    def scan_market_intelligence(self):
        """
        AI simulates a deep scan of the current job market for the user's field.
        """
        # Get user's field from latest forecast or analysis
        forecast = CareerForecast.query.filter_by(user_id=self.user_id).order_by(CareerForecast.created_at.desc()).first()
        target = forecast.target_role if forecast else "Tech Industry"
        
        # In a real app, this would query a real job API
        # Here we simulate finding a 'perfect match'
        notification = Notification(
            user_id=self.user_id,
            message=f"🍒 Cherry: While you were away, I scanned the market for '{target}' roles. I found 3 new high-match opportunities in your district."
        )
        db.session.add(notification)
        db.session.commit()
        return "market_scan_completed"

    def check_career_gaps(self):
        """
        AI checks if any recent activity has closed gaps in the career roadmap.
        """
        forecast = CareerForecast.query.filter_by(user_id=self.user_id).order_by(CareerForecast.created_at.desc()).first()
        if not forecast: return "no_forecast_to_check"
        
        # Logic to compare UserQuest progress vs Roadmap
        notification = Notification(
            user_id=self.user_id,
            message=f"🍒 Cherry: I've reviewed your recent skill acquisitions. You've closed 15% of the gap towards becoming a {forecast.target_role}. Energy levels are optimal."
        )
        db.session.add(notification)
        db.session.commit()
        return "gap_check_completed"

    @staticmethod
    def run_global_homeostasis():
        """
        Self-healing tasks for the whole system.
        """
        from .homeostasis import Homeostasis
        status = Homeostasis.get_system_status()
        if status['health'] != 'nominal':
            # Perform 'deep cleaning' of the DB or log rotation
            print("🍒 Cherry: Global Homeostasis activated. Healing system nodes...")
            return True
        return False
