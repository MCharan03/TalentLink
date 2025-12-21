import streamlit as st
import smtplib
from email.mime.text import MIMEText
from logger_config import logger


def send_email(to_address, subject, body):
    """Sends an email using the configured SMTP settings."""
    try:
        smtp_server = st.secrets["email"]["smtp_server"]
        smtp_port = st.secrets["email"]["smtp_port"]
        smtp_user = st.secrets["email"]["smtp_user"]
        smtp_password = st.secrets["email"]["smtp_password"]

        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = smtp_user
        msg['To'] = to_address

        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.sendmail(smtp_user, [to_address], msg.as_string())
        logger.info(f"Successfully sent email to {to_address}")
        return True
    except smtplib.SMTPException as e:
        logger.error(f"SMTP error sending email to {to_address}: {e}")
        st.error(f"SMTP error: {e}")
        return False
    except KeyError:
        logger.error("Email settings not found in secrets.toml")
        st.error(
            "Email settings not found in secrets.toml. Please configure them to send emails.")
        return False
    except Exception as e:
        logger.error(f"An unexpected error occurred while sending email: {e}")
        st.error(f"An unexpected error occurred while sending email: {e}")
        return False
