from flask_socketio import emit
from app.extensions import socketio, db
from flask import request, session, url_for
from flask_login import current_user
from app.models import UserData, MockInterview
from app.utils.ai_utils import get_interview_question, generate_interview_report
import json

@socketio.on('connect')
def handle_connect():
    print(f"Client connected: {request.sid}")
    emit('status', {'msg': 'Connected to AI Interview Coach'})

@socketio.on('disconnect')
def handle_disconnect():
    print(f"Client disconnected: {request.sid}")

@socketio.on('start_interview')
def handle_start_interview(data):
    print(f"DEBUG: Starting interview for SID: {request.sid}")
    
    # Initialize transcript in session
    session['interview_transcript'] = []
    
    if current_user.is_authenticated:
        user_data = UserData.query.filter_by(user_id=current_user.id).order_by(UserData.uploaded_at.desc()).first()
        if user_data and user_data.analysis_result:
            context = {
                'field': user_data.analysis_result.get('predicted_field', 'General'),
                'level': user_data.analysis_result.get('experience_level', 'N/A'),
                'skills': user_data.analysis_result.get('actual_skills', []),
                'summary': user_data.analysis_result.get('ai_summary', '')[:500]
            }
            session['interview_context'] = json.dumps(context)
        else:
            session['interview_context'] = None
            
    question = get_interview_question("Tell me about yourself.", "start")
    
    # Record first question
    session['interview_transcript'].append(f"AI: {question}")
    session.modified = True
    
    emit('interview_question', {'question': question})

@socketio.on('send_answer')
def handle_send_answer(data):
    answer = data.get('answer', '')
    transcript = session.get('interview_transcript', [])
    transcript.append(f"User: {answer}")
    
    context_json = session.get('interview_context')
    context = json.loads(context_json) if context_json else None
    
    question = get_interview_question(answer, "continue", resume_context=context)
    
    transcript.append(f"AI: {question}")
    session['interview_transcript'] = transcript
    session.modified = True
    
    emit('interview_question', {'question': question})

@socketio.on('end_interview')
def handle_end_interview(data):
    """
    Finalizes the interview, generates the report, and saves to DB.
    """
    transcript_list = session.get('interview_transcript', [])
    if not transcript_list:
        emit('report_ready', {'error': 'No transcript found.'})
        return
        
    full_transcript = "\n".join(transcript_list)
    
    # Generate AI Report
    report = generate_interview_report(full_transcript)
    
    if report and current_user.is_authenticated:
        # Save to database
        interview_record = MockInterview(
            user_id=current_user.id,
            transcript=full_transcript,
            feedback=json.dumps(report),
            score=report.get('overall_score', 0)
        )
        db.session.add(interview_record)
        db.session.commit()
        
        # Notify frontend
        emit('report_ready', {
            'redirect_url': url_for('user.interview_report', interview_id=interview_record.id)
        })
    else:
        emit('report_ready', {'error': 'Failed to generate report or user not logged in.'})
