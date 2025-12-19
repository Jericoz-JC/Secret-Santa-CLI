"""Email sending via Brevo (SendinBlue) API."""

from typing import Optional
import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException

from .models import Assignment, Config


class EmailError(Exception):
    """Raised when email sending fails."""
    pass


def create_email_html(receiver_name: str, gift_limit: int = 25, verification_code: str = "") -> str:
    """Create festive HTML email content."""
    return f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #1a472a 0%, #2d5a3f 100%);
            margin: 0;
            padding: 40px 20px;
        }}
        .container {{
            max-width: 500px;
            margin: 0 auto;
            background: #fff;
            border-radius: 16px;
            padding: 40px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.3);
        }}
        .header {{
            text-align: center;
            margin-bottom: 30px;
        }}
        .snowflakes {{
            font-size: 40px;
            letter-spacing: 10px;
        }}
        h1 {{
            color: #c41e3a;
            margin: 20px 0 10px;
            font-size: 28px;
        }}
        .gift-box {{
            background: linear-gradient(135deg, #c41e3a 0%, #8b0000 100%);
            color: white;
            padding: 30px;
            border-radius: 12px;
            text-align: center;
            margin: 30px 0;
        }}
        .gift-box .label {{
            font-size: 14px;
            opacity: 0.9;
            margin-bottom: 10px;
        }}
        .gift-box .name {{
            font-size: 32px;
            font-weight: bold;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }}
        .info-box {{
            background: #f8f9fa;
            border: 2px solid #28a745;
            padding: 20px;
            border-radius: 12px;
            text-align: center;
            margin: 20px 0;
        }}
        .info-box .limit {{
            font-size: 24px;
            font-weight: bold;
            color: #28a745;
        }}
        .verification {{
            background: #fff3cd;
            border: 2px solid #ffc107;
            padding: 15px;
            border-radius: 8px;
            text-align: center;
            margin: 20px 0;
        }}
        .verification .code {{
            font-size: 28px;
            font-weight: bold;
            font-family: monospace;
            color: #856404;
            letter-spacing: 4px;
        }}
        .footer {{
            text-align: center;
            color: #666;
            font-size: 14px;
            margin-top: 30px;
        }}
        .tree {{
            font-size: 50px;
            text-align: center;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="snowflakes">❄️ ⛄ ❄️</div>
            <h1>🎄 Secret Santa 🎄</h1>
            <p>You've been matched!</p>
        </div>
        
        <div class="gift-box">
            <div class="label">You are buying a gift for:</div>
            <div class="name">🎁 {receiver_name} 🎁</div>
        </div>
        
        <div class="info-box">
            <div>💰 Gift Limit</div>
            <div class="limit">${gift_limit}</div>
        </div>
        
        <div class="verification">
            <div>🔐 Your Verification Code</div>
            <div class="code">{verification_code}</div>
            <div style="font-size: 12px; color: #666; margin-top: 10px;">Use this code to verify your assignment is correct</div>
        </div>
        
        <div class="footer">
            <div class="tree">🎄</div>
            <p>Remember: Keep it a secret! 🤫</p>
            <p>Happy Holidays!</p>
        </div>
    </div>
</body>
</html>
"""


def send_assignment_email(
    assignment: Assignment,
    config: Config,
    dry_run: bool = False
) -> dict:
    """
    Send a Secret Santa assignment email.
    
    Args:
        assignment: The assignment to send
        config: Email configuration with API key
        dry_run: If True, don't actually send, just return what would be sent
    
    Returns:
        Dict with send details
    
    Raises:
        EmailError: If sending fails
    """
    if not config.brevo_api_key:
        raise EmailError("Brevo API key not configured. Run: santa config --api-key YOUR_KEY")
    
    if not config.sender_email:
        raise EmailError("Sender email not configured. Run: santa config --sender-email YOUR_EMAIL")
    
    html_content = create_email_html(
        assignment.receiver_name,
        gift_limit=config.gift_limit,
        verification_code=assignment.verification_code
    )
    subject = "🎄 Your Secret Santa Assignment!"
    
    to_list = [{"email": assignment.giver_email, "name": assignment.giver_name}]
    cc_list = []
    
    if assignment.parent_email:
        cc_list.append({"email": assignment.parent_email, "name": "Parent"})
    
    result = {
        "to": assignment.giver_email,
        "cc": assignment.parent_email,
        "subject": subject,
        "giver": assignment.giver_name,
        "receiver": assignment.receiver_name,
        "dry_run": dry_run,
    }
    
    if dry_run:
        result["status"] = "would_send"
        return result
    
    # Configure Brevo API
    configuration = sib_api_v3_sdk.Configuration()
    configuration.api_key['api-key'] = config.brevo_api_key
    
    api_instance = sib_api_v3_sdk.TransactionalEmailsApi(
        sib_api_v3_sdk.ApiClient(configuration)
    )
    
    send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
        to=to_list,
        cc=cc_list if cc_list else None,
        sender={"email": config.sender_email, "name": config.sender_name},
        subject=subject,
        html_content=html_content,
    )
    
    try:
        api_response = api_instance.send_transac_email(send_smtp_email)
        result["status"] = "sent"
        result["message_id"] = api_response.message_id
    except ApiException as e:
        raise EmailError(f"Failed to send email: {e}")
    
    return result


def send_all_assignments(
    assignments: list[Assignment],
    config: Config,
    dry_run: bool = False,
    on_progress: Optional[callable] = None
) -> list[dict]:
    """
    Send emails for all assignments.
    
    Args:
        assignments: List of assignments to send
        config: Email configuration
        dry_run: If True, don't actually send
        on_progress: Optional callback(assignment, result) for progress updates
    
    Returns:
        List of send results
    """
    results = []
    
    for assignment in assignments:
        if assignment.email_sent and not dry_run:
            results.append({
                "to": assignment.giver_email,
                "status": "already_sent",
                "giver": assignment.giver_name,
            })
            continue
        
        try:
            result = send_assignment_email(assignment, config, dry_run)
            results.append(result)
            
            if on_progress:
                on_progress(assignment, result)
                
        except EmailError as e:
            results.append({
                "to": assignment.giver_email,
                "status": "error",
                "error": str(e),
                "giver": assignment.giver_name,
            })
    
    return results
