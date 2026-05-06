import os
import base64
import json
import cv2
import numpy as np
from datetime import datetime
from backend.extensions import db, socketio
from backend.models import SkillFitAssessment, EmotionalState
from backend.utils.ai_utils import _call_gemini

# Attempt to import face_recognition (might fail if not installed in current environment)
try:
    import face_recognition
except ImportError:
    face_recognition = None

class SkillFitService:
    def __init__(self):
        self.active_sessions = {} # user_id -> session_data

    def start_assessment(self, user_id, job_id=None, language='Kannada'):
        self.active_sessions[user_id] = {
            'job_id': job_id,
            'language': language,
            'audio_buffer': [],
            'video_frames': [],
            'transcript': [],
            'start_time': datetime.utcnow(),
            'fraud_flags': set(), # Use set to avoid duplicates
            'face_confidence_scores': []
        }
        return "Assessment started."

    def process_chunk(self, user_id, data):
        if user_id not in self.active_sessions:
            return
        
        session = self.active_sessions[user_id]
        
        # 1. Store Audio Buffer
        if 'audio' in data:
            session['audio_buffer'].append(data['audio'])
            
        # 2. Process Video Frame (Deep Validation)
        if 'video_frame' in data:
            frame_data = data['video_frame']
            # Sampling: Deep validate only occasionally to save CPU
            if len(session['video_frames']) % 10 == 0:
                self._deep_validate_frame(user_id, frame_data)
            session['video_frames'].append(frame_data)

    def _deep_validate_frame(self, user_id, frame_b64):
        if not face_recognition:
            return

        session = self.active_sessions[user_id]
        try:
            # Decode base64 image
            encoded_data = frame_b64.split(',')[1]
            nparr = np.frombuffer(base64.b64decode(encoded_data), np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if img is None:
                return

            # RGB for face_recognition
            rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            
            # 1. Face Count Check
            face_locations = face_recognition.face_locations(rgb_img)
            if len(face_locations) > 1:
                session['fraud_flags'].add("Multiple faces detected in frame")
            elif len(face_locations) == 0:
                session['fraud_flags'].add("Face not visible during session")
                
            # 2. Simple 'Spoofing' check - Blur/Static Detection
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
            if laplacian_var < 10: # Extremely blurry or static
                session['fraud_flags'].add("Low quality / potential static image detected")
                
        except Exception as e:
            print(f"Error in deep validation: {e}")

    def finalize_assessment(self, user_id):
        if user_id not in self.active_sessions:
            return None
        
        session = self.active_sessions[user_id]
        
        # Multimodal Assessment using Gemini 1.5 Pro
        # Simulate processing the audio/video buffer
        
        prompt = f"""
        Analyze this AI SkillFit Video Interview.
        Language: {session['language']}
        Fraud Flags Detected by Vision Layer: {list(session['fraud_flags'])}
        
        Based on the candidate's responses:
        1. Categorize fitment: Job-ready, Requires Training, Requires Manual Verification, or Low-confidence.
        2. Evaluate Relevance (0-1), Clarity (0-1), Confidence (0-1).
        3. Explain the reasoning.
        
        Output JSON:
        {{
            "fitment_category": "...",
            "relevance_score": 0.0,
            "clarity_score": 0.0,
            "confidence_score": 0.0,
            "overall_score": 0.0,
            "reasoning": "...",
            "language_detected": "...",
            "dialect_detected": "..."
        }}
        """
        
        # result = _call_gemini(prompt, response_mime_type='application/json')
        
        # Mocking for prototype
        result = {
            "fitment_category": "Job-ready" if not session['fraud_flags'] else "Requires Manual Verification",
            "relevance_score": 0.85,
            "clarity_score": 0.75,
            "confidence_score": 0.80,
            "overall_score": 0.80,
            "reasoning": "Candidate demonstrated technical proficiency in Kannada. Vision layer flagged minor visibility issues." if session['fraud_flags'] else "Strong candidate with clear communication in local dialect.",
            "language_detected": "Kannada",
            "dialect_detected": "Mysore/Mandya"
        }
        
        assessment = SkillFitAssessment(
            user_id=user_id,
            job_id=session['job_id'],
            language=result['language_detected'],
            dialect=result['dialect_detected'],
            relevance_score=result['relevance_score'],
            clarity_score=result['clarity_score'],
            confidence_score=result['confidence_score'],
            overall_score=result['overall_score'],
            fitment_category=result['fitment_category'],
            fraud_flags=list(session['fraud_flags']),
            face_confidence=0.88,
            voice_confidence=0.90,
            transcript_summary=result['reasoning']
        )
        
        db.session.add(assessment)
        db.session.commit()
        
        del self.active_sessions[user_id]
        return assessment.id

skillfit_service = SkillFitService()
