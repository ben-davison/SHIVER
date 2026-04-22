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
    <p>This link will expire in 48 hours.</p>
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
        
        
async def send_cube_failed_email(email_to: str, region: str, error_reason: str = "An unexpected server error occurred."):
    html = f"""
    <div style="font-family: sans-serif; color: #333;">
        <h3 style="color: #f44336;">SHIVER Data Cube Generation Failed</h3>
        <p>We are sorry, but your requested data cube for <b>{region}</b> could not be generated.</p>
        
        <div style="background-color: #fce4e4; border: 1px solid #fccacb; padding: 15px; border-radius: 5px; margin: 20px 0;">
            <strong>Reason for failure:</strong><br/>
            {error_reason}
        </div>
        
        <p>Please adjust your request parameters and try again. If the issue persists, contact the SHIVER support team.</p>
    </div>
    """

    message = MessageSchema(
        subject="SHIVER Data Extraction Failed",
        recipients=[email_to],
        body=html,
        subtype="html"
    )

    fm = FastMail(conf)
    try:
        await fm.send_message(message) 
        print(f"Failure email sent to {email_to}")
    except Exception as e:
        print(f"Failed to send failure email: {e}")
        

async def send_password_reset_email(email_to: str, token: str):
    # CHANGE THIS if your frontend runs on a different port/domain in production
    frontend_base_url = "http://localhost:5173" 
    reset_link = f"{frontend_base_url}/reset-password?token={token}"

    html = f"""
    <h3>SHIVER Password Reset</h3>
    <p>We received a request to reset your password.</p>
    <p>Click the link below to set a new password:</p>
    <p>
      <a href="{reset_link}" style="padding: 10px 20px; background: #e74c3c; color: white; text-decoration: none; border-radius: 5px;">
        Reset Password
      </a>
    </p>
    <p>Or copy this link: {reset_link}</p>
    <p>If you did not request this, please ignore this email.</p>
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