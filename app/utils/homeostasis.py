from datetime import datetime, timedelta
from app.models import db, SystemMetric, SystemSetting
from flask import current_app

class Homeostasis:
    @staticmethod
    def log_error(route, error_message=None):
        """Logs an error metric for a specific route."""
        try:
            metric = SystemMetric(
                metric_type='error',
                route=route,
                value=1.0,
                timestamp=datetime.utcnow()
            )
            db.session.add(metric)
            db.session.commit()
            
            # After logging, check if we need to trigger self-healing
            Homeostasis.check_system_health()
        except Exception as e:
            print(f"Failed to log error metric: {e}")

    @staticmethod
    def check_system_health():
        """Checks for error spikes and updates system health / maintenance mode."""
        if SystemSetting.get_setting('self_healing_enabled') != 'true':
            return

        threshold = int(SystemSetting.get_setting('error_threshold_per_minute', 10))
        one_minute_ago = datetime.utcnow() - timedelta(minutes=1)
        
        error_count = SystemMetric.query.filter(
            SystemMetric.metric_type == 'error',
            SystemMetric.timestamp >= one_minute_ago
        ).count()

        health_setting = SystemSetting.query.filter_by(key='system_health').first()
        
        if error_count > threshold:
            if health_setting:
                health_setting.value = 'critical'
            # Trigger emergency lockdown if extremely high
            if error_count > threshold * 2:
                maint_mode = SystemSetting.query.filter_by(key='maintenance_mode').first()
                if maint_mode:
                    maint_mode.value = 'true'
                    print(f"EMERGENCY: Error spike detected ({error_count}). Maintenance mode ENABLED.")
        elif error_count > threshold / 2:
            if health_setting:
                health_setting.value = 'stressed'
        else:
            if health_setting:
                health_setting.value = 'nominal'
        
        db.session.commit()

    @staticmethod
    def is_route_sick(route):
        """Returns True if a specific route has a high failure rate recently."""
        # Simple implementation: if more than 5 errors in last 5 minutes for this route
        five_minutes_ago = datetime.utcnow() - timedelta(minutes=5)
        error_count = SystemMetric.query.filter(
            SystemMetric.metric_type == 'error',
            SystemMetric.route == route,
            SystemMetric.timestamp >= five_minutes_ago
        ).count()
        
        return error_count >= 5

    @staticmethod
    def get_system_status():
        """Returns overall system health and maintenance status for the frontend."""
        import os
        ai_provider = os.environ.get("CURRENT_AI_PROVIDER", "ollama")
        
        return {
            'health': SystemSetting.get_setting('system_health', 'nominal'),
            'maintenance': SystemSetting.get_setting('maintenance_mode', 'false') == 'true',
            'ai_node': "Local Node (Ollama)" if ai_provider == "ollama" else "Cloud Core (Gemini)",
            'error_count_1m': SystemMetric.query.filter(
                SystemMetric.metric_type == 'error',
                SystemMetric.timestamp >= (datetime.utcnow() - timedelta(minutes=1))
            ).count()
        }
