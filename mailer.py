import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

def send_email(to, subject, body):
    sg_key = os.getenv("SENDGRID_API_KEY")
    sender = os.getenv("SENDER_EMAIL")

    if not sg_key or not sender:
        print("SendGrid not configured")
        return

    message = Mail(
        from_email=sender,
        to_emails=to,
        subject=subject,
        plain_text_content=body
    )

    try:
        sg = SendGridAPIClient(sg_key)
        sg.send(message)
        print("Email sent successfully")
    except Exception as e:
        print("SendGrid error:", e)
