from backend import create_app, db
from backend.models import User, UserXP, RecruiterProfile, Organization, Society, Notification
from backend.services.gamification_service import gamification_service

app = create_app()

def seed_users():
    with app.app_context():
        print("Seeding societies and organizations...")
        
        # Create Society
        society = Society.query.filter_by(name="Global Tech Collective").first()
        if not society:
            society = Society(name="Global Tech Collective", description="A high-level network of industry leaders.")
            db.session.add(society)
            db.session.flush()
        else:
            print("Society 'Global Tech Collective' already exists.")

        # Create Organization
        org = Organization.query.filter_by(name="TalentLink AI").first()
        if not org:
            society_id = society.id if society else None
            org = Organization(name="TalentLink AI", website="https://talentlink.ai", 
                              description="Leading AI-driven career solutions.", society_id=society_id)
            db.session.add(org)
            db.session.flush()
        else:
            print("Organization 'TalentLink AI' already exists.")
        
        db.session.commit()

        # 1. Admin
        admin_email = 'admin@talentlink.ai'
        admin_username = 'admin_talentlink' # Changed to avoid conflict
        admin = User.query.filter((User.email == admin_email) | (User.username == admin_username)).first()
        if not admin:
            admin = User(username=admin_username, email=admin_email, role='admin', is_verified=True)
            admin.set_password('admin_pass')
            db.session.add(admin)
            db.session.commit()
            print(f"Admin created: {admin_email} / admin_pass")
        else:
            print(f"Admin already exists: {admin.email} ({admin.username})")

        # 2. Recruiter
        rec_email = 'recruiter@talentlink.ai'
        rec_username = 'recruiter_jane'
        recruiter = User.query.filter((User.email == rec_email) | (User.username == rec_username)).first()
        if not recruiter:
            recruiter = User(username=rec_username, email=rec_email, role='recruiter', is_verified=True)
            recruiter.set_password('recruiter_pass')
            db.session.add(recruiter)
            db.session.commit()
            
            rec_profile = RecruiterProfile(user_id=recruiter.id, organization_id=org.id, 
                                          department="Engineering", is_verified=True)
            db.session.add(rec_profile)
            db.session.commit()
            print(f"Recruiter created: {rec_email} / recruiter_pass")
        else:
            print(f"Recruiter already exists: {recruiter.email} ({recruiter.username})")

        # 3. Candidate
        cand_email = 'candidate@talentlink.ai'
        cand_username = 'john_doe'
        candidate = User.query.filter((User.email == cand_email) | (User.username == cand_username)).first()
        if not candidate:
            candidate = User(username=cand_username, email=cand_email, role='user', is_verified=True)
            candidate.set_password('candidate_pass')
            db.session.add(candidate)
            db.session.commit()
            
            gamification_service.initialize_user_xp(candidate.id)
            
            notification = Notification(user_id=candidate.id, message="Welcome to the Smart Resume Analyzer!")
            db.session.add(notification)
            db.session.commit()
            print(f"Candidate created: {cand_email} / candidate_pass")
        else:
            print(f"Candidate already exists: {candidate.email} ({candidate.username})")

        print("\nAll test users seeded successfully.")

if __name__ == "__main__":
    seed_users()
