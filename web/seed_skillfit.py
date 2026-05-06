from backend import create_app, db
from backend.models import SkillFitAssessment, User
from datetime import datetime

app = create_app()

def seed_skillfit():
    with app.app_context():
        user = User.query.filter_by(role='user').first()
        if not user:
            print("No user found to associate assessment with.")
            return

        print("Seeding sample SkillFit assessments...")
        
        a1 = SkillFitAssessment(
            user_id=user.id,
            language="Kannada",
            dialect="North Karnataka",
            relevance_score=0.9,
            clarity_score=0.8,
            confidence_score=0.85,
            overall_score=0.85,
            fitment_category="Job-ready",
            fraud_flags=[],
            face_confidence=0.98,
            voice_confidence=0.95,
            transcript_summary="Candidate demonstrated excellent proficiency in electrical wiring and safety protocols."
        )

        a2 = SkillFitAssessment(
            user_id=user.id,
            language="Kannada",
            dialect="Mysore",
            relevance_score=0.6,
            clarity_score=0.5,
            confidence_score=0.4,
            overall_score=0.5,
            fitment_category="Requires Training",
            fraud_flags=["Face not visible during session"],
            face_confidence=0.4,
            voice_confidence=0.8,
            transcript_summary="Candidate has basic knowledge but lacks communication clarity. Vision layer flagged visibility issues."
        )

        db.session.add(a1)
        db.session.add(a2)
        db.session.commit()
        print("Done.")

if __name__ == "__main__":
    seed_skillfit()
