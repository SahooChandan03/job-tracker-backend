from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
from .index import settings



def send_email(email_to: str, subject: str, html_content: str) -> None:
    print({
        "email" : settings.FROM_EMAIL,
        "host" : settings.SMTP_HOST,
        "port": settings.SMTP_PORT,
        "user":settings.SMTP_USER,
        "key": settings.SMTP_KEY
    })
    msg = MIMEMultipart()
    msg["From"] = settings.FROM_EMAIL
    msg["To"] = email_to
    msg["Subject"] = subject
    msg.attach(MIMEText(html_content, "html"))

    try:
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            server.starttls()
            # For Brevo, use the SMTP API key as password
            server.login(settings.SMTP_USER, settings.SMTP_KEY)
            server.send_message(msg)
        print("Email sent successfully!")
    except smtplib.SMTPAuthenticationError as e:
        print(f"SMTP Authentication failed: {e}")
        print("Please check your Brevo SMTP credentials")
    except Exception as e:
        print(f"Failed to send email: {e}")


def send_email_via_brevo_api(email_to: str, subject: str, html_content: str) -> None:
    """Send email using Brevo's HTTP API instead of SMTP"""
    import requests
    
    try:
        url = "https://api.brevo.com/v3/smtp/email"
        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "api-key": settings.SMTP_KEY  # Use your regular API key here
        }
        
        payload = {
            "sender": {
                "name": "Job Tracker",
                "email": settings.FROM_EMAIL
            },
            "to": [
                {
                    "email": email_to
                }
            ],
            "subject": subject,
            "htmlContent": html_content
        }
        
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        print("Email sent successfully via Brevo API!")
        
    except Exception as e:
        print(f"Failed to send email via Brevo API: {e}")
def send_otp_email(email_to: str, otp: str) -> None:
    subject = "Your OTP Code"
    html_content = f"""
    <html>
        <body>
            <h1>Your OTP Code</h1>
            <p>Your OTP code is: <strong>{otp}</strong></p>
            <p>This code will expire in {settings.OTP_EXPIRY_SECONDS // 60} minutes.</p>
        </body>
    </html>
    """
    # print the html content
    print(html_content,"html_content",email_to,"email_to",subject,"subject")
    # Use Brevo API instead of SMTP for better reliability
    send_email_via_brevo_api(email_to=email_to, subject=subject, html_content=html_content)

def send_password_reset_email(email_to: str, reset_token: str) -> None:
    subject = "Password Reset Request"
    html_content = f"""
    <html>
        <body>
            <h1>Password Reset Request</h1>
            <p>Click the link below to reset your password:</p>
            <p><a href="http://your-frontend-url/reset-password?token={reset_token}">Reset Password</a></p>
            <p>This link will expire in {settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES} minutes.</p>
        </body>
    </html>
    """
    # Use Brevo API instead of SMTP for better reliability
    send_email_via_brevo_api(email_to=email_to, subject=subject, html_content=html_content) 