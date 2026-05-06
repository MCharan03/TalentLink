from flask_mail import Message
from flask import current_app
from ..extensions import mail
from threading import Thread


def send_async_email(app, msg):
    with app.app_context():
        try:
            print(f"Sending async email to {msg.recipients}...")
            mail.send(msg)
            print("Async email sent successfully.")
        except Exception as e:
            print(f"Failed to send async email: {e}")


def send_email(to, subject, template, category='default', **kwargs):
    app = current_app._get_current_object()
    print(f"Preparing to send email to {to} [category={category}]")
    
    # Select sender based on category
    senders = app.config.get('EMAIL_SENDERS', {})
    # Priority: Category-specific -> Default Sender -> Mail Username (Authenticated User)
    sender = senders.get(category) or app.config.get('MAIL_DEFAULT_SENDER') or app.config.get('MAIL_USERNAME')
    
    msg = Message(subject, sender=sender, recipients=[to])
    # msg.body = render_template(template + '.txt', **kwargs)
    # msg.html = render_template(template + '.html', **kwargs)
    # For now, just sending simple text if template is not handled or assuming content is passed
    msg.body = kwargs.get('body', '')
    if 'html' in kwargs:
        msg.html = kwargs['html']

    try:
        thr = Thread(target=send_async_email, args=[app, msg])
        thr.start()
        print(f"Thread started for email to {to}")
        return thr
    except Exception as e:
        print(f"Error starting email thread: {e}")
        return None
