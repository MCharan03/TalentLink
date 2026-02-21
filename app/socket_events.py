from flask_socketio import emit
from app.extensions import socketio, db
from flask import request, session, url_for
from flask_login import current_user
from app.services.interview_service import interview_service
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
    
    # Fetch Context via Service
    if current_user.is_authenticated:
        context = interview_service.get_user_context(current_user.id)
        session['interview_context'] = json.dumps(context) if context else None
    else:
        session['interview_context'] = None
            
    # Generate First Question
    question = interview_service.get_next_question("Tell me about yourself.", "start")
    
    # Record first question
    session['interview_transcript'].append(f"AI: {question}")
    session.modified = True
    
    emit('interview_question', {'question': question})

@socketio.on('send_answer')
def handle_send_answer(data):
    answer = data.get('answer', '')
    transcript = session.get('interview_transcript', [])
    
    # Identify the last question asked by AI for context
    last_ai_question = "Tell me about yourself." # Default
    if transcript:
        for entry in reversed(transcript):
            if entry.startswith("AI: "):
                last_ai_question = entry.replace("AI: ", "")
                break
    
    transcript.append(f"User: {answer}")
    
    # 1. Real-time Sentiment Analysis (The "Sentient" Layer)
    # We do this *before* generating the next question to give immediate feedback
    analysis = interview_service.analyze_response(last_ai_question, answer)
    emit('sentiment_feedback', analysis)
    
    context_json = session.get('interview_context')
    context = json.loads(context_json) if context_json else None
    
    # 2. Get Next Question via Service
    question = interview_service.get_next_question(answer, "continue", context=context)
    
    transcript.append(f"AI: {question}")
    session['interview_transcript'] = transcript
    session.modified = True
    
    emit('interview_question', {'question': question})

@socketio.on('end_interview')
def handle_end_interview(data):
    """
    Finalizes the interview using the service.
    """
    transcript_list = session.get('interview_transcript', [])
    
    if not current_user.is_authenticated:
        emit('report_ready', {'error': 'User not logged in.'})
        return

    interview_id, error = interview_service.finalize_interview(current_user, transcript_list)
    
    if interview_id:
        emit('report_ready', {
            'redirect_url': url_for('user.interview_report', interview_id=interview_id)
        })
    else:
        emit('report_ready', {'error': error or 'Failed to generate report.'})
