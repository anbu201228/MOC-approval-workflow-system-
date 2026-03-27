from app import app, mail
from flask_mail import Message
import sys

def test_email():
    print("Testing email configuration...")
    with app.app_context():
        try:
            msg = Message(
                subject="Test Email from MOC System",
                recipients=["anbukkarasan2004@gmail.com"],  # Sending to the sender for testing
                body="This is a test email to verify SMTP settings."
            )
            mail.send(msg)
            print("✓ Email sent successfully.")
        except Exception as e:
            print(f"✗ Email failed: {e}")
            sys.exit(1)

if __name__ == "__main__":
    test_email()
