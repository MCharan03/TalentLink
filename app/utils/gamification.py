from ..extensions import db
from ..models import UserXP, UserQuest, Quest, Notification, SystemSetting
from datetime import datetime

def award_xp(user, amount, reason=None):
    """Awards XP to a user and handles leveling up."""
    # Check for Global Multiplier
    multiplier = 1.0
    try:
        setting = SystemSetting.query.filter_by(key='xp_multiplier').first()
        if setting:
            multiplier = float(setting.value)
    except:
        pass # Fallback to 1.0
        
    final_amount = int(amount * multiplier)
    
    xp_profile = UserXP.query.filter_by(user_id=user.id).first()
    if not xp_profile:
        xp_profile = UserXP(user_id=user.id, total_xp=0, level=1)
        db.session.add(xp_profile)
    
    xp_profile.total_xp += final_amount
    
    # Simple Leveling Logic: 100 XP per level
    new_level = (xp_profile.total_xp // 100) + 1
    if new_level > xp_profile.level:
        xp_profile.level = new_level
        # Send level up notification
        notif = Notification(
            user_id=user.id,
            message=f"🎉 Level Up! You are now Level {new_level}."
        )
        db.session.add(notif)
    
    if reason:
        msg = f"✨ Gained {final_amount} XP for {reason}."
        if multiplier > 1.0:
            msg += f" (includes {multiplier}x Event Bonus!)"
            
        notif = Notification(
            user_id=user.id,
            message=msg
        )
        db.session.add(notif)
    
    db.session.commit()
    return xp_profile

def check_quest_progress(user, action_type):
    """Checks and updates user quest progress based on an action."""
    active_quests = UserQuest.query.filter_by(user_id=user.id, status='in_progress').all()
    
    for uq in active_quests:
        quest = Quest.query.get(uq.quest_id)
        criteria = quest.criteria
        
        if criteria.get('type') == action_type:
            # Update progress
            current_progress = uq.progress.get('count', 0)
            new_progress = current_progress + 1
            uq.progress['count'] = new_progress
            
            # Check if completed
            if new_progress >= criteria.get('count', 1):
                uq.status = 'completed'
                uq.completed_at = datetime.utcnow()
                award_xp(user, quest.xp_reward, f"completing quest: {quest.title}")
    
    db.session.commit()

def init_default_quests():
    """Seeds the database with standard quests."""
    default_quests = [
        {"title": "The First Step", "description": "Upload and analyze your first resume.", "xp": 50, "criteria": {"type": "resume_analysis", "count": 1}},
        {"title": "Code Warrior", "description": "Perform a GitHub Audit.", "xp": 100, "criteria": {"type": "github_audit", "count": 1}},
        {"title": "Interview Ready", "description": "Complete 3 Mock Tests.", "xp": 150, "criteria": {"type": "mock_test", "count": 3}},
        {"title": "Job Hunter", "description": "Apply for 5 jobs.", "xp": 200, "criteria": {"type": "job_apply", "count": 5}}
    ]
    
    for q_data in default_quests:
        if not Quest.query.filter_by(title=q_data['title']).first():
            q = Quest(
                title=q_data['title'],
                description=q_data['description'],
                xp_reward=q_data['xp'],
                criteria=q_data['criteria']
            )
            db.session.add(q)
    db.session.commit()
