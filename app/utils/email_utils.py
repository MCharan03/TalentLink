from flask_mail import Message
from flask import current_app
from ..extensions import mail
from threading import Thread


def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)


def send_email(to, subject, template, category='default', **kwargs):
    app = current_app._get_current_object()
    
    # Select sender based on category
    senders = app.config.get('EMAIL_SENDERS', {})
    sender = senders.get(category, senders.get('default', app.config.get('ADMIN_EMAIL')))
    
    msg = Message(subject, sender=sender, recipients=[to])
    # msg.body = render_template(template + '.txt', **kwargs)
    # msg.html = render_template(template + '.html', **kwargs)
    # For now, just sending simple text if template is not handled or assuming content is passed
    msg.body = kwargs.get('body', '')
    if 'html' in kwargs:
        msg.html = kwargs['html']

    thr = Thread(target=send_async_email, args=[app, msg])
    thr.start()
    return thr
