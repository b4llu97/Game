import os
import logging
import requests
from typing import Optional

logger = logging.getLogger(__name__)

class NotificationService:
    def __init__(self):
        self.telegram_token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.telegram_chat_id = os.getenv("TELEGRAM_CHAT_ID")
        self.toolserver_url = os.getenv("TOOLSERVER_URL", "http://toolserver:8002")
        
        self.telegram_enabled = bool(self.telegram_token and self.telegram_chat_id)
        
        if not self.telegram_enabled:
            logger.warning("Telegram not configured (missing TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID)")
        else:
            logger.info("Telegram notifications enabled")
    
    def send_notification(self, message: str, priority: str = "normal") -> bool:
        if not self.telegram_enabled:
            logger.info(f"[SIMULATED] Would send: {message}")
            return True
        
        try:
            success = self._send_telegram(message)
            if success:
                logger.info(f"Notification sent successfully: {message[:50]}...")
            return success
        except Exception as e:
            logger.error(f"Failed to send notification: {e}")
            return False
    
    def _send_telegram(self, message: str) -> bool:
        try:
            url = f"https://api.telegram.org/bot{self.telegram_token}/sendMessage"
            payload = {
                "chat_id": self.telegram_chat_id,
                "text": message,
                "parse_mode": "HTML"
            }
            
            response = requests.post(url, json=payload, timeout=10)
            response.raise_for_status()
            
            return True
        except Exception as e:
            logger.error(f"Telegram API error: {e}")
            return False
    
    def test_connection(self) -> bool:
        if not self.telegram_enabled:
            logger.info("Telegram not enabled, skipping test")
            return False
        
        return self._send_telegram("🤖 Jarvis Proaktiv-Engine Test-Nachricht")
