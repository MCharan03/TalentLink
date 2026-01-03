from app import create_app, db
from app.models import UserData, User
from sqlalchemy import func
from collections import Counter

app = create_app()

with app.app_context():
    print("--- Checking UserData ---")
    user_data = UserData.query.order_by(UserData.uploaded_at.desc()).all()
    print(f"Total UserData: {len(user_data)}")
    
    fields = []
    levels = []
    all_skills = []
    
    for entry in user_data:
        res = entry.analysis_result
        if res:
            fields.append(res.get('predicted_field', 'Unknown'))
            levels.append(res.get('experience_level', 'Unknown'))
            skills = res.get('actual_skills', [])
            if isinstance(skills, list):
                all_skills.extend([s.lower() for s in skills])
    
    print(f"Fields found: {fields}")
    print(f"Levels found: {levels}")
    print(f"Skills count: {len(all_skills)}")

    field_counts = dict(Counter(fields))
    level_counts = dict(Counter(levels))
    skill_counts = dict(Counter(all_skills).most_common(10))
    
    print(f"Field Counts: {field_counts}")
    print(f"Level Counts: {level_counts}")
    print(f"Skill Counts (top 10): {skill_counts}")

    print("\n--- Checking Timeline Aggregation ---")
    try:
        # SQLite specific date extraction might differ or behave differently
        analysis_dates = db.session.query(func.date(UserData.uploaded_at), func.count(UserData.id)).group_by(func.date(UserData.uploaded_at)).all()
        print(f"Raw analysis_dates query result: {analysis_dates}")
        
        engagement_dates = []
        for d in analysis_dates:
            date_val = d[0]
            print(f"Processing date: {date_val} (type: {type(date_val)})")
            if isinstance(date_val, str):
                engagement_dates.append(date_val)
            elif date_val:
                 engagement_dates.append(date_val.strftime('%Y-%m-%d'))
            else:
                engagement_dates.append('')
        
        analysis_counts = [d[1] for d in analysis_dates]
        print(f"Final Engagement Dates: {engagement_dates}")
        print(f"Final Analysis Counts: {analysis_counts}")
    except Exception as e:
        print(f"Error in timeline aggregation: {e}")