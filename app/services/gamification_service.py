from app.models import UserXP, Quest, UserQuest, db
from app.models import User
from datetime import datetime

class GamificationService:
    def initialize_user_xp(self, user_id):
        """Creates a UserXP profile if it doesn't exist."""
        if not UserXP.query.filter_by(user_id=user_id).first():
            xp_profile = UserXP(user_id=user_id, total_xp=0, level=1)
            db.session.add(xp_profile)
            db.session.commit()

    def award_synergy_bonus(self, user_id):
        """
        Awards a 'Sentient Synergy' bonus for interacting with AI nodes.
        This reinforces the 'Sentient OS' theme and encourages engagement.
        """
        xp_profile = UserXP.query.filter_by(user_id=user_id).first()
        if not xp_profile:
            self.initialize_user_xp(user_id)
            xp_profile = UserXP.query.filter_by(user_id=user_id).first()

        # Small 5 XP bonus with a cap per session (simulated here)
        bonus = 5
        xp_profile.total_xp += bonus
        
        # Leveling check
        new_level = 1 + (xp_profile.total_xp // 100)
        if new_level > xp_profile.level:
            xp_profile.level = new_level
        
        db.session.commit()
        return xp_profile.total_xp, xp_profile.level

    def award_xp(self, user_id, amount, reason="action"):
        """Awards XP and handles leveling up."""
        xp_profile = UserXP.query.filter_by(user_id=user_id).first()
        if not xp_profile:
            self.initialize_user_xp(user_id)
            xp_profile = UserXP.query.filter_by(user_id=user_id).first()

        xp_profile.total_xp += amount
        
        # Drain energy on action (e.g., 5% per action)
        if xp_profile.energy > 0:
            xp_profile.energy = max(0, xp_profile.energy - 5)

        # Simple leveling logic: Level = 1 + (XP / 100)
        new_level = 1 + (xp_profile.total_xp // 100)
        if new_level > xp_profile.level:
            xp_profile.level = new_level
            # TODO: Emit a "Level Up" event via SocketIO
        
        db.session.commit()
        return xp_profile.total_xp, xp_profile.level

    def replenish_energy(self, user_id, amount=100):
        """Replenishes user energy."""
        xp_profile = UserXP.query.filter_by(user_id=user_id).first()
        if xp_profile:
            xp_profile.energy = min(100, xp_profile.energy + amount)
            db.session.commit()
        return xp_profile.energy if xp_profile else 100

    def check_quests(self, user_id, event_type):
        """
        Checks if any quests are completed based on an event.
        event_type: e.g., 'upload_resume', 'complete_interview'
        """
        # This is a simplified logic. In a real RPG, we'd have a more complex rule engine.
        quests = Quest.query.filter(Quest.criteria.like(f'%"{event_type}"%')).all()
        
        completed_quests = []
        for quest in quests:
            # Check if user already completed it
            user_quest = UserQuest.query.filter_by(user_id=user_id, quest_id=quest.id).first()
            if user_quest and user_quest.status == 'completed':
                continue
            
            # If not, mark as completed (assuming 1-time action for now)
            if not user_quest:
                user_quest = UserQuest(user_id=user_id, quest_id=quest.id, status='completed', completed_at=datetime.utcnow())
                db.session.add(user_quest)
                self.award_xp(user_id, quest.xp_reward, reason=f"Quest: {quest.title}")
                completed_quests.append(quest.title)
            else:
                user_quest.status = 'completed'
                user_quest.completed_at = datetime.utcnow()
                self.award_xp(user_id, quest.xp_reward)
                completed_quests.append(quest.title)
        
        db.session.commit()
        return completed_quests

gamification_service = GamificationService()
