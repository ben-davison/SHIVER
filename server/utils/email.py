# web/server/utils/email.py
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from dependencies import MAIL_USERNAME, MAIL_PASSWORD, MAIL_FROM, MAIL_PORT, MAIL_SERVER, FRONTEND_URL
import json

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
        

async def send_dev_error_email(user_email: str, region: str, raw_error: str, payload_data: dict):
    """
    Sends a detailed diagnostic report to the dev team when an unhandled 
    exception occurs during background processing.
    """
    dev_email = "shiver@sheffield.ac.uk"
    
    # Format the payload dictionary into a clean, indented JSON string
    try:
        pretty_payload = json.dumps(payload_data, indent=4)
    except Exception:
        pretty_payload = str(payload_data)

    # Developer-friendly HTML layout using monospace blocks for debugging
    html = f"""
    <div style="font-family: sans-serif; color: #333; line-height: 1.6; max-width: 800px;">
        <h3 style="color: #d32f2f; border-bottom: 2px solid #d32f2f; padding-bottom: 8px; margin-top: 0;">
            [BUG REPORT] SHIVER Backend Exception
        </h3>
        <p>An unhandled server error occurred during a multi-source data cube background task.</p>
        
        <table style="border-collapse: collapse; width: 100%; margin: 15px 0; font-size: 14px;">
            <tr>
                <td style="padding: 8px; border: 1px solid #ddd; font-weight: bold; width: 150px; background-color: #f9f9f9;">User Email:</td>
                <td style="padding: 8px; border: 1px solid #ddd;">{user_email}</td>
            </tr>
            <tr>
                <td style="padding: 8px; border: 1px solid #ddd; font-weight: bold; background-color: #f9f9f9;">Detected Region:</td>
                <td style="padding: 8px; border: 1px solid #ddd;">{region}</td>
            </tr>
        </table>

        <h4 style="color: #c62828; margin-bottom: 5px;">Raw Python Error:</h4>
        <pre style="background-color: #fbe9e7; border: 1px solid #ffccbc; padding: 12px; border-radius: 4px; overflow-x: auto; font-family: monospace; color: #c62828; font-size: 13px; margin-top: 0;">{raw_error}</pre>

        <h4 style="color: #2e7d32; margin-bottom: 5px;">User Request Payload:</h4>
        <pre style="background-color: #efebe9; border: 1px solid #d7ccc8; padding: 12px; border-radius: 4px; overflow-x: auto; font-family: monospace; color: #3e2723; font-size: 13px; margin-top: 0;">{pretty_payload}</pre>
    </div>
    """

    message = MessageSchema(
        subject=f"SHIVER Error Notification: {region} Multi-Source Cube",
        recipients=[dev_email],
        body=html,
        subtype="html"
    )

    fm = FastMail(conf)
    try:
        await fm.send_message(message) 
        print(f"Developer error alert successfully sent to {dev_email}")
    except Exception as e:
        # Fallback to console print if the mail server itself drops the connection
        print(f"CRITICAL: Failed to send developer alert email: {e}")
        

async def send_password_reset_email(email_to: str, token: str):
    # Pass the token as a query parameter on your main page URL
    reset_link = f"{FRONTEND_URL}/?reset_token={token}"

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