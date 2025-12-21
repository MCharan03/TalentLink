from flask_mail import Message
from flask import current_app
from ..extensions import mail
from threading import Thread


def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)


def send_email(to, subject, template, **kwargs):
    app = current_app._get_current_object()
    msg = Message(subject, sender=app.config['ADMIN_EMAIL'], recipients=[to])
    # msg.body = render_template(template + '.txt', **kwargs)
    # msg.html = render_template(template + '.html', **kwargs)
    # For now, just sending simple text if template is not handled or assuming content is passed
    msg.body = kwargs.get('body', '')
    if 'html' in kwargs:
        msg.html = kwargs['html']

    thr = Thread(target=send_async_email, args=[app, msg])
    thr.start()
    return thr
