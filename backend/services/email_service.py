"""
Email Service using Resend API

Sends contract change alert emails to users.
"""
from resend import Resend
from typing import Optional
from database import get_settings
from logger import get_logger

logger = get_logger(__name__)


class EmailService:
    """Service for sending emails via Resend."""
    
    def __init__(self):
        settings = get_settings()
        self.client = Resend(api_key=settings.resend_api_key)
        self.from_email = "alerts@contractdrifter.com"
    
    def send_alert_email(
        self,
        to_email: str,
        vendor: str,
        change_type: str,
        risk_level: str,
        risk_score: int,
        explanation: str,
        contract_id: str,
        change_id: str
    ) -> bool:
        """
        Send contract change alert email.
        
        Args:
            to_email: Recipient email address
            vendor: Vendor name
            change_type: Type of change (added, removed, modified, rewritten)
            risk_level: Risk level (critical, high, medium, low)
            risk_score: Risk score 0-100
            explanation: AI-generated explanation
            contract_id: Contract UUID
            change_id: Change UUID
            
        Returns:
            True if email sent successfully, False otherwise
        """
        try:
            # Determine color based on risk level
            risk_colors = {
                "critical": "#dc2626",
                "high": "#f97316",
                "medium": "#f59e0b",
                "low": "#10b981"
            }
            color = risk_colors.get(risk_level, "#64748b")
            
            # Build email subject
            subject = f"🚨 {risk_level.upper()} Risk Alert: {vendor} Contract Changed"
            
            # Build HTML email content
            html_content = f"""
            <!DOCTYPE html>
            <html>
              <head>
                <meta charset="utf-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
              </head>
              <body style="margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;">
                <table width="100%" cellpadding="0" cellspacing="0" style="background-color: #f8fafc; padding: 40px 20px;">
                  <tr>
                    <td align="center">
                      <table width="600" cellpadding="0" cellspacing="0" style="background-color: #ffffff; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);">
                        
                        <!-- Header -->
                        <tr>
                          <td style="background-color: {color}; padding: 30px; text-align: center;">
                            <h1 style="margin: 0; color: #ffffff; font-size: 24px; font-weight: 700;">
                              Contract Change Detected
                            </h1>
                          </td>
                        </tr>
                        
                        <!-- Content -->
                        <tr>
                          <td style="padding: 30px;">
                            <h2 style="margin: 0 0 20px 0; color: #1e293b; font-size: 20px; font-weight: 600;">
                              Vendor: {vendor}
                            </h2>
                            
                            <!-- Change Details Box -->
                            <table width="100%" cellpadding="15" cellspacing="0" style="background-color: #f8fafc; border-radius: 8px; margin-bottom: 20px;">
                              <tr>
                                <td>
                                  <p style="margin: 0 0 10px 0; color: #475569; font-size: 14px;">
                                    <strong>Change Type:</strong> <span style="text-transform: uppercase; color: #1e293b;">{change_type}</span>
                                  </p>
                                  <p style="margin: 0 0 10px 0; color: #475569; font-size: 14px;">
                                    <strong>Risk Level:</strong> <span style="color: {color}; font-weight: 600; text-transform: uppercase;">{risk_level}</span>
                                  </p>
                                  <p style="margin: 0; color: #475569; font-size: 14px;">
                                    <strong>Risk Score:</strong> {risk_score}/100
                                  </p>
                                </td>
                              </tr>
                            </table>
                            
                            <!-- Explanation Box -->
                            <table width="100%" cellpadding="15" cellspacing="0" style="background-color: #fef2f2; border-left: 4px solid {color}; border-radius: 4px; margin-bottom: 25px;">
                              <tr>
                                <td>
                                  <h3 style="margin: 0 0 10px 0; color: #1e293b; font-size: 16px; font-weight: 600;">
                                    Why This Matters:
                                  </h3>
                                  <p style="margin: 0; color: #475569; font-size: 14px; line-height: 1.6;">
                                    {explanation}
                                  </p>
                                </td>
                              </tr>
                            </table>
                            
                            <!-- CTA Button -->
                            <table width="100%" cellpadding="0" cellspacing="0">
                              <tr>
                                <td align="center">
                                  <a href="http://localhost:3000/contracts?id={contract_id}" 
                                     style="display: inline-block; background-color: #4f46e5; color: #ffffff; padding: 14px 28px; text-decoration: none; border-radius: 8px; font-weight: 600; font-size: 14px;">
                                    Review Contract Changes →
                                  </a>
                                </td>
                              </tr>
                            </table>
                          </td>
                        </tr>
                        
                        <!-- Footer -->
                        <tr>
                          <td style="background-color: #f8fafc; padding: 20px; text-align: center; border-top: 1px solid #e2e8f0;">
                            <p style="margin: 0; color: #64748b; font-size: 12px;">
                              Contract Drifter - Automated Contract Monitoring
                            </p>
                            <p style="margin: 5px 0 0 0; color: #94a3b8; font-size: 11px;">
                              Change ID: {change_id[:8]}...
                            </p>
                          </td>
                        </tr>
                        
                      </table>
                    </td>
                  </tr>
                </table>
              </body>
            </html>
            """
            
            # Send email via Resend
            response = self.client.emails.send({
                "from": self.from_email,
                "to": [to_email],
                "subject": subject,
                "html": html_content,
            })
            
            logger.info(f"Email sent successfully to {to_email}: {response['id']}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {e}")
            return False
    
    def send_test_email(self, to_email: str) -> bool:
        """Send a test email to verify configuration."""
        return self.send_alert_email(
            to_email=to_email,
            vendor="Test Vendor",
            change_type="modified",
            risk_level="high",
            risk_score=85,
            explanation="This is a test email to verify your Contract Drifter email configuration is working correctly.",
            contract_id="00000000-0000-0000-0000-000000000000",
            change_id="00000000-0000-0000-0000-000000000001"
        )
