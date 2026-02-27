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
    
    # Get interview config from client
    interview_type = data.get('interview_type', 'mixed')
    difficulty = data.get('difficulty', 'medium')
    
    # Initialize session state
    session['interview_transcript'] = []
    session['interview_round'] = 1
    session['interview_type'] = interview_type
    session['interview_difficulty'] = difficulty
    
    # Fetch Context via Service
    if current_user.is_authenticated:
        context = interview_service.get_user_context(current_user.id)
        session['interview_context'] = json.dumps(context) if context else None
    else:
        session['interview_context'] = None
            
    # Generate First Question
    question = interview_service.get_next_question(
        "Tell me about yourself.", "start",
        interview_type=interview_type,
        difficulty=difficulty,
        round_number=1
    )
    
    # Record first question
    session['interview_transcript'].append(f"AI: {question}")
    session.modified = True
    
    emit('interview_question', {
        'question': question,
        'round': 1,
        'interview_type': interview_type,
        'difficulty': difficulty
    })

@socketio.on('send_answer')
def handle_send_answer(data):
    answer = data.get('answer', '')
    transcript = session.get('interview_transcript', [])
    round_number = session.get('interview_round', 1)
    interview_type = session.get('interview_type', 'mixed')
    difficulty = session.get('interview_difficulty', 'medium')
    
    # Identify the last question asked by AI for context
    last_ai_question = "Tell me about yourself."  # Default
    if transcript:
        for entry in reversed(transcript):
            if entry.startswith("AI: "):
                last_ai_question = entry.replace("AI: ", "")
                break
    
    transcript.append(f"User: {answer}")
    
    # 1. Real-time Sentiment & STAR Analysis
    analysis = interview_service.analyze_response(
        last_ai_question, answer, interview_type=interview_type
    )
    analysis['round'] = round_number
    emit('sentiment_feedback', analysis)
    
    context_json = session.get('interview_context')
    context = json.loads(context_json) if context_json else None
    
    # Increment round
    round_number += 1
    session['interview_round'] = round_number
    
    # 2. Get Next Question via Service with full context
    question = interview_service.get_next_question(
        answer, "continue",
        context=context,
        interview_type=interview_type,
        difficulty=difficulty,
        round_number=round_number,
        conversation_history=transcript[-6:]  # Last 3 Q&A pairs
    )
    
    transcript.append(f"AI: {question}")
    session['interview_transcript'] = transcript
    session.modified = True
    
    emit('interview_question', {
        'question': question,
        'round': round_number,
        'interview_type': interview_type,
        'difficulty': difficulty
    })

@socketio.on('end_interview')
def handle_end_interview(data):
    """
    Finalizes the interview using the service.
    """
    transcript_list = session.get('interview_transcript', [])
    interview_type = session.get('interview_type', 'mixed')
    difficulty = session.get('interview_difficulty', 'medium')
    
    if not current_user.is_authenticated:
        emit('report_ready', {'error': 'User not logged in.'})
        return

    interview_id, error = interview_service.finalize_interview(
        current_user, transcript_list,
        interview_type=interview_type,
        difficulty=difficulty
    )
    
    if interview_id:
        emit('report_ready', {
            'redirect_url': url_for('user.interview_report', interview_id=interview_id)
        })
    else:
        emit('report_ready', {'error': error or 'Failed to generate report.'})
