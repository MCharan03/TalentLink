from flask_socketio import emit
from app.extensions import socketio
from app.services.interview_service import interview_coach
from flask import request

@socketio.on('connect')
def handle_connect():
    print(f"Client connected: {request.sid}")
    emit('status', {'msg': 'Connected to AI Interview Coach'})

@socketio.on('analyze_answer')
def handle_answer_analysis(data):
    """
    Expects data: {'question': '...', 'answer': '...'}
    """
    question = data.get('question')
    answer = data.get('answer')
    
    if not question or not answer:
        emit('coach_feedback', {'error': 'Missing question or answer'})
        return

    # Call Gemini service
    try:
        feedback = interview_coach.analyze_response(question, answer)
        emit('coach_feedback', feedback)
    except Exception as e:
        emit('coach_feedback', {'error': str(e)})

@socketio.on('disconnect')
def handle_disconnect():
    print(f"Client disconnected: {request.sid}")
