import os
import time
import logging
from threading import Thread
from file_watcher import FileWatcher
from mail_fetcher import MailFetcher

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    logger.info("Starting Jarvis Ingestion Service...")
    
    nas_path = os.getenv("NAS_MOUNT_PATH", "/mnt/nas")
    enable_mail_fetch = os.getenv("ENABLE_MAIL_FETCH", "false").lower() == "true"
    
    file_watcher = FileWatcher(watch_path=nas_path)
    
    file_watcher_thread = Thread(target=file_watcher.start, daemon=True)
    file_watcher_thread.start()
    logger.info(f"File watcher started for: {nas_path}")
    
    if enable_mail_fetch:
        mail_fetcher = MailFetcher()
        mail_fetcher_thread = Thread(target=mail_fetcher.start, daemon=True)
        mail_fetcher_thread.start()
        logger.info("Mail fetcher started")
    else:
        logger.info("Mail fetcher disabled (ENABLE_MAIL_FETCH=false)")
    
    try:
        while True:
            time.sleep(60)
    except KeyboardInterrupt:
        logger.info("Shutting down ingestion service...")

if __name__ == "__main__":
    main()
