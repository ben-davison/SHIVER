# web/server/utils/email.py
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from dependencies import MAIL_USERNAME, MAIL_PASSWORD, MAIL_FROM, MAIL_PORT, MAIL_SERVER

conf = ConnectionConfig(
    MAIL_USERNAME=MAIL_USERNAME,
    MAIL_PASSWORD=MAIL_PASSWORD,
    MAIL_FROM=MAIL_FROM,
    MAIL_PORT=MAIL_PORT,
    MAIL_SERVER=MAIL_SERVER,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False
)

async def send_cube_ready_email(email_to: str, download_link: str, region: str):
    html = f"""
    <h3>SHIVER Data Cube Ready</h3>
    <p>Your requested data cube for <b>{region}</b> is ready.</p>
    <p>
      <a href="{download_link}" style="padding: 10px 20px; background: #00ccff; color: white; text-decoration: none; border-radius: 5px;">
        Download Data
      </a>
    </p>
    <p>Or copy this link: {download_link}</p>
    """

    message = MessageSchema(
        subject="Your SHIVER Data Cube is Ready",
        recipients=[email_to],
        body=html,
        subtype="html"
    )

    fm = FastMail(conf)
    
    try:
        # Connect to Gmail and send
        print(f"Sending email to {email_to}...")
        await fm.send_message(message) 
        print(f"Email successfully sent!")
    except Exception as e:
        print(f"Failed to send email: {e}")
        

async def send_password_reset_email(email_to: str, token: str):
    # CHANGE THIS if your frontend runs on a different port/domain in production
    frontend_base_url = "http://localhost:5173" 
    reset_link = f"{frontend_base_url}/reset-password?token={token}"

    html = f"""
    <h3>SHIVER Password Reset</h3>
    <p>We received a request to reset your password.</p>
    <p>Click the link below to set a new password:</p>
    <p>
      <a href="{reset_link}" style="padding: 10px 20px; background: #e74c3c; color: white; text-decoration: none; border-radius: 5px; display: inline-block; margin: 10px 0px;">
        Reset Password
      </a>
    </p>
    <p>Or copy this link: <br><a href="{reset_link}">{reset_link}</a></p>
    <p><strong>Please note:</strong> This password reset link will expire in 1 hour.</p>
    <p>If you did not request this, please ignore this email. Your password will remain unchanged.</p>
    """

    message = MessageSchema(
        subject="Reset Your SHIVER Password",
        recipients=[email_to],
        body=html,
        subtype="html"
    )

    fm = FastMail(conf)
    
    try:
        print(f"Sending reset email to {email_to}...")
        await fm.send_message(message) 
        print(f"Reset email sent!")
    except Exception as e:
        print(f"Failed to send reset email: {e}")