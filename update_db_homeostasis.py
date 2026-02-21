from app import create_app, db
from app.models import SystemSetting, UserXP
from sqlalchemy import text

app = create_app()

def update_schema():
    with app.app_context():
        # Check if energy column exists in user_xp
        try:
            db.session.execute(text("SELECT energy FROM user_xp LIMIT 1"))
        except Exception:
            print("Adding energy column to user_xp...")
            db.session.execute(text("ALTER TABLE user_xp ADD COLUMN energy INTEGER DEFAULT 100"))
            db.session.commit()

        # Create tables if not exist (e.g. SystemMetric)
        db.create_all()

        # Seed initial system settings
        settings = [
            {'key': 'maintenance_mode', 'value': 'false', 'description': 'Master switch for global maintenance mode'},
            {'key': 'error_threshold_per_minute', 'value': '10', 'description': 'Errors per minute before route lockdown'},
            {'key': 'self_healing_enabled', 'value': 'true', 'description': 'Enable autonomous route lockdown and healing'},
            {'key': 'system_health', 'value': 'nominal', 'description': 'Overall system health: nominal, stressed, critical'}
        ]

        for s in settings:
            if not SystemSetting.query.filter_by(key=s['key']).first():
                setting = SystemSetting(key=s['key'], value=s['value'], description=s['description'])
                db.session.add(setting)
        
        db.session.commit()
        print("Database schema and settings updated successfully.")

if __name__ == "__main__":
    update_schema()
