import os
import yaml
import logging
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

class RulesEngine:
    def __init__(self):
        self.toolserver_url = os.getenv("TOOLSERVER_URL", "http://toolserver:8002")
        self.config_path = os.getenv("PROACTIVITY_CONFIG", "/app/config/proactivity.yml")
        self.rules = self._load_rules()
    
    def _load_rules(self) -> Dict[str, Any]:
        if not os.path.exists(self.config_path):
            logger.warning(f"Config file not found: {self.config_path}, using defaults")
            return self._get_default_rules()
        
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                rules = yaml.safe_load(f)
                logger.info(f"Loaded rules from {self.config_path}")
                return rules or self._get_default_rules()
        except Exception as e:
            logger.error(f"Failed to load rules: {e}")
            return self._get_default_rules()
    
    def _get_default_rules(self) -> Dict[str, Any]:
        return {
            "reminders": {
                "morning": [
                    {
                        "type": "tax_deadline",
                        "check_fact": "naechste_steuer_frist",
                        "days_before": 7,
                        "message": "⚠️ Erinnerung: Steuer-Frist in {days} Tagen"
                    }
                ],
                "evening": [
                    {
                        "type": "appointment",
                        "check_fact": "naechster_termin",
                        "hours_before": 24,
                        "message": "📅 Morgen: {appointment_name} um {time}"
                    }
                ]
            }
        }
    
    def get_due_reminders(self, time_window: str) -> List[Dict[str, Any]]:
        reminders = []
        
        window_rules = self.rules.get("reminders", {}).get(time_window, [])
        
        for rule in window_rules:
            try:
                reminder = self._check_rule(rule, time_window)
                if reminder:
                    reminders.append(reminder)
            except Exception as e:
                logger.error(f"Error checking rule {rule.get('type')}: {e}")
        
        return reminders
    
    def _check_rule(self, rule: Dict[str, Any], time_window: str) -> Optional[Dict[str, Any]]:
        rule_type = rule.get("type")
        
        if rule_type == "tax_deadline":
            return self._check_tax_deadline(rule)
        elif rule_type == "appointment":
            return self._check_appointment(rule)
        
        return None
    
    def _check_tax_deadline(self, rule: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        fact_key = rule.get("check_fact", "naechste_steuer_frist")
        days_before = rule.get("days_before", 7)
        
        fact_value = self._get_fact(fact_key)
        if not fact_value:
            return None
        
        try:
            deadline = datetime.fromisoformat(fact_value)
            days_until = (deadline - datetime.now()).days
            
            if 0 <= days_until <= days_before:
                message = rule.get("message", "Steuer-Frist bald fällig")
                message = message.format(days=days_until)
                
                return {
                    "type": "tax_deadline",
                    "message": message,
                    "priority": "high" if days_until <= 3 else "normal"
                }
        except Exception as e:
            logger.error(f"Error parsing tax deadline: {e}")
        
        return None
    
    def _check_appointment(self, rule: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        fact_key = rule.get("check_fact", "naechster_termin")
        hours_before = rule.get("hours_before", 24)
        
        fact_value = self._get_fact(fact_key)
        if not fact_value:
            return None
        
        try:
            parts = fact_value.split("|")
            if len(parts) < 2:
                return None
            
            appointment_time = datetime.fromisoformat(parts[0].strip())
            appointment_name = parts[1].strip()
            
            hours_until = (appointment_time - datetime.now()).total_seconds() / 3600
            
            if 0 <= hours_until <= hours_before:
                message = rule.get("message", "Termin steht an")
                message = message.format(
                    appointment_name=appointment_name,
                    time=appointment_time.strftime("%H:%M")
                )
                
                return {
                    "type": "appointment",
                    "message": message,
                    "priority": "normal"
                }
        except Exception as e:
            logger.error(f"Error parsing appointment: {e}")
        
        return None
    
    def _get_fact(self, key: str) -> Optional[str]:
        try:
            response = requests.get(
                f"{self.toolserver_url}/v1/facts/{key}",
                timeout=5
            )
            if response.status_code == 200:
                data = response.json()
                return data.get("value")
            elif response.status_code == 404:
                logger.debug(f"Fact not found: {key}")
            else:
                logger.warning(f"Unexpected response for fact {key}: {response.status_code}")
        except Exception as e:
            logger.error(f"Error fetching fact {key}: {e}")
        
        return None
