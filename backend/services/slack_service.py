"""
Slack Service for sending notifications

Sends contract change alerts to Slack channels via webhooks.
"""
import requests
from typing import Optional
from database import get_settings
from logger import get_logger

logger = get_logger(__name__)


class SlackService:
    """Service for sending Slack notifications."""
    
    def __init__(self):
        settings = get_settings()
        self.webhook_url = settings.slack_webhook_url
    
    def send_alert(
        self,
        channel: str,
        vendor: str,
        change_type: str,
        risk_level: str,
        risk_score: int,
        explanation: str,
        contract_id: str
    ) -> bool:
        """
        Send contract change alert to Slack.
        
        Args:
            channel: Slack channel (e.g., #contract-alerts)
            vendor: Vendor name
            change_type: Type of change
            risk_level: Risk level (critical, high, medium, low)
            risk_score: Risk score 0-100
            explanation: AI-generated explanation
            contract_id: Contract UUID
            
        Returns:
            True if sent successfully, False otherwise
        """
        try:
            # Color based on risk level
            color_map = {
                "critical": "#dc2626",
                "high": "#f97316",
                "medium": "#f59e0b",
                "low": "#10b981"
            }
            color = color_map.get(risk_level, "#64748b")
            
            # Emoji based on risk level
            emoji_map = {
                "critical": ":rotating_light:",
                "high": ":warning:",
                "medium": ":large_orange_diamond:",
                "low": ":information_source:"
            }
            emoji = emoji_map.get(risk_level, ":bell:")
            
            # Build Slack message
            message = {
                "channel": channel,
                "username": "Contract Drifter",
                "icon_emoji": ":scroll:",
                "attachments": [{
                    "color": color,
                    "title": f"{emoji} {risk_level.upper()} Risk Alert: {vendor}",
                    "title_link": f"http://localhost:3000/contracts?id={contract_id}",
                    "fields": [
                        {
                            "title": "Change Type",
                            "value": change_type.upper(),
                            "short": True
                        },
                        {
                            "title": "Risk Score",
                            "value": f"{risk_score}/100",
                            "short": True
                        },
                        {
                            "title": "Why This Matters",
                            "value": explanation,
                            "short": False
                        }
                    ],
                    "footer": "Contract Drifter",
                    "footer_icon": "https://platform.slack-edge.com/img/default_application_icon.png",
                    "ts": int(__import__('time').time())
                }]
            }
            
            # Send to Slack
            response = requests.post(
                self.webhook_url,
                json=message,
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()
            
            logger.info(f"Slack alert sent to {channel} for {vendor}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send Slack alert: {e}")
            return False
    
    def send_test_message(self, channel: str = "#general") -> bool:
        """Send a test message to verify configuration."""
        return self.send_alert(
            channel=channel,
            vendor="Test Vendor",
            change_type="modified",
            risk_level="high",
            risk_score=85,
            explanation="This is a test message to verify your Contract Drifter Slack integration is working correctly.",
            contract_id="00000000-0000-0000-0000-000000000000"
        )
