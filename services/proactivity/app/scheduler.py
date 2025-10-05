import os
import logging
from datetime import datetime, time
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from rules_engine import RulesEngine
from notifications import NotificationService

logger = logging.getLogger(__name__)

class ProactivityScheduler:
    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.rules_engine = RulesEngine()
        self.notification_service = NotificationService()
        
        self.time_windows = [
            {"start": time(7, 30), "end": time(8, 30), "name": "morning"},
            {"start": time(18, 30), "end": time(20, 0), "name": "evening"}
        ]
        
        self.notification_counts = {
            "morning": 0,
            "evening": 0
        }
        
        self.max_notifications_per_window = 3
        
        self._setup_jobs()
    
    def _setup_jobs(self):
        self.scheduler.add_job(
            self._morning_check,
            CronTrigger(hour=7, minute=30),
            id="morning_check",
            name="Morning Proactivity Check"
        )
        
        self.scheduler.add_job(
            self._evening_check,
            CronTrigger(hour=18, minute=30),
            id="evening_check",
            name="Evening Proactivity Check"
        )
        
        self.scheduler.add_job(
            self._reset_daily_counters,
            CronTrigger(hour=0, minute=0),
            id="reset_counters",
            name="Reset Daily Counters"
        )
        
        logger.info("Scheduled jobs configured")
    
    def _is_in_time_window(self):
        now = datetime.now().time()
        for window in self.time_windows:
            if window["start"] <= now <= window["end"]:
                return window["name"]
        return None
    
    def _can_send_notification(self, window_name):
        if window_name is None:
            return False
        return self.notification_counts.get(window_name, 0) < self.max_notifications_per_window
    
    def _increment_notification_count(self, window_name):
        if window_name:
            self.notification_counts[window_name] = self.notification_counts.get(window_name, 0) + 1
    
    def _morning_check(self):
        logger.info("Running morning proactivity check")
        window_name = "morning"
        
        if not self._can_send_notification(window_name):
            logger.info(f"Max notifications reached for {window_name} window")
            return
        
        reminders = self.rules_engine.get_due_reminders("morning")
        
        for reminder in reminders:
            if self._can_send_notification(window_name):
                success = self.notification_service.send_notification(
                    message=reminder["message"],
                    priority=reminder.get("priority", "normal")
                )
                if success:
                    self._increment_notification_count(window_name)
                    logger.info(f"Sent morning reminder: {reminder['message'][:50]}...")
    
    def _evening_check(self):
        logger.info("Running evening proactivity check")
        window_name = "evening"
        
        if not self._can_send_notification(window_name):
            logger.info(f"Max notifications reached for {window_name} window")
            return
        
        reminders = self.rules_engine.get_due_reminders("evening")
        
        for reminder in reminders:
            if self._can_send_notification(window_name):
                success = self.notification_service.send_notification(
                    message=reminder["message"],
                    priority=reminder.get("priority", "normal")
                )
                if success:
                    self._increment_notification_count(window_name)
                    logger.info(f"Sent evening reminder: {reminder['message'][:50]}...")
    
    def _reset_daily_counters(self):
        logger.info("Resetting daily notification counters")
        self.notification_counts = {
            "morning": 0,
            "evening": 0
        }
    
    def start(self):
        self.scheduler.start()
        logger.info("Proactivity scheduler started")
    
    def shutdown(self):
        self.scheduler.shutdown()
        logger.info("Proactivity scheduler shut down")
    
    def is_running(self):
        return self.scheduler.running
    
    def get_active_time_windows(self):
        current_window = self._is_in_time_window()
        return {
            "current_window": current_window,
            "windows": [
                {
                    "name": w["name"],
                    "start": w["start"].strftime("%H:%M"),
                    "end": w["end"].strftime("%H:%M")
                }
                for w in self.time_windows
            ]
        }
    
    def get_notification_count(self):
        return self.notification_counts
