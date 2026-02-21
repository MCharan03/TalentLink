from flask import render_template, send_from_directory, current_app, jsonify, request, session
from flask_login import login_required, current_user
from . import main
from ..extensions import db
from ..utils.ai_utils import _call_gemini
from ..utils.agent import CareerAgent
import time

@main.route('/')
def index():
    return render_template('index.html')


@main.route('/flowchart')
def flowchart():
    return render_template('main/flowchart.html')

# --- Gemini Chatbot Helper ---
@main.route('/api/chatbot', methods=['POST'])
def api_chatbot():
    data = request.get_json()
    user_message = data.get('message')
    history = data.get('history', [])
    
    if not user_message:
        return jsonify({'error': 'Message required'}), 400

    # 1. Rate Limiting (Simple: Max 10 messages per minute)
    now = time.time()
    chat_history = session.get('chat_timestamps', [])
    chat_history = [t for t in chat_history if now - t < 60]
    
    if len(chat_history) >= 10:
        return jsonify({'error': 'Rate limit exceeded. Please wait a moment.'}), 429
        
    chat_history.append(now)
    session['chat_timestamps'] = chat_history

    try:
        reply = ""
        if current_user.is_authenticated:
            # Use Advanced Agent with Context
            formatted_history = []
            for h in history:
                role = 'user' if h['role'] in ['user', 'You'] else 'model' # Handle 'You' from frontend if sent
                formatted_history.append({'role': role, 'parts': [h['content']]})
                
            agent = CareerAgent(current_user)
            reply = agent.chat(user_message, formatted_history)
        else:
            # Basic fallback for visitors
            system_prompt = "You are a helpful Career Assistant for the 'Smart Resume Analyzer' app. You help users with resume tips, interview prep, and navigating the site. Keep answers concise (under 100 words)."
            full_prompt = f"{system_prompt}\n\nUser: {user_message}\nAssistant:"
            reply = _call_gemini(full_prompt)
        
        if not reply:
             return jsonify({'error': 'AI is busy. Try again.'}), 500

        return jsonify({'reply': reply})
        
    except Exception as e:
        print(f"Chatbot Error: {e}")
        return jsonify({'error': 'AI is busy. Try again.'}), 500


@main.route('/mark_notifications_read', methods=['POST'])
@login_required
def mark_notifications_read():
    from ..models import Notification
    unread = current_user.notifications.filter_by(is_read=False).all()
    for n in unread:
        n.is_read = True
    db.session.commit()
    return jsonify({'status': 'success'})


@main.route('/notifications/<int:notif_id>/delete', methods=['POST'])
@login_required
def delete_notification(notif_id):
    from ..models import Notification
    n = Notification.query.get_or_404(notif_id)
    if n.user_id != current_user.id:
        return jsonify({'status': 'error', 'message': 'Forbidden'}), 403

    was_unread = not n.is_read
    db.session.delete(n)
    db.session.commit()
    return jsonify({'status': 'success', 'was_unread': was_unread})


from ..decorators import self_healing_gate

@main.route('/stress_test')
@self_healing_gate
def stress_test():
    """Deliberately unstable route to test self-healing."""
    error_mode = request.args.get('error', 'false') == 'true'
    if error_mode:
        # This will trigger the 500 handler, which logs to Homeostasis
        raise Exception("Neural overload in the stress-test sector!")
    
    return "Stress test sector stable. Add ?error=true to overload."


@main.route('/uploads/<path:filename>')
def uploaded_file(filename):
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)
