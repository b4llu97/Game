import os
import time
import email
import logging
from email.header import decode_header
from imaplib import IMAP4_SSL
from document_processor import DocumentProcessor

logger = logging.getLogger(__name__)

class MailFetcher:
    def __init__(self):
        self.imap_server = os.getenv("IMAP_SERVER", "")
        self.imap_user = os.getenv("IMAP_USER", "")
        self.imap_password = os.getenv("IMAP_PASSWORD", "")
        self.imap_folder = os.getenv("IMAP_FOLDER", "INBOX")
        self.fetch_interval = int(os.getenv("MAIL_FETCH_INTERVAL", "300"))
        self.processor = DocumentProcessor()
    
    def start(self):
        if not self.imap_server or not self.imap_user or not self.imap_password:
            logger.warning("IMAP credentials not configured. Mail fetcher will not run.")
            return
        
        logger.info(f"Mail fetcher configured for: {self.imap_user}@{self.imap_server}")
        
        while True:
            try:
                self._fetch_new_emails()
            except Exception as e:
                logger.error(f"Error fetching emails: {e}")
            
            time.sleep(self.fetch_interval)
    
    def _fetch_new_emails(self):
        try:
            mail = IMAP4_SSL(self.imap_server)
            mail.login(self.imap_user, self.imap_password)
            mail.select(self.imap_folder)
            
            status, messages = mail.search(None, 'UNSEEN')
            
            if status != 'OK':
                logger.warning("No new emails found")
                mail.close()
                mail.logout()
                return
            
            email_ids = messages[0].split()
            
            for email_id in email_ids:
                try:
                    status, msg_data = mail.fetch(email_id, '(RFC822)')
                    
                    if status != 'OK':
                        continue
                    
                    for response_part in msg_data:
                        if isinstance(response_part, tuple):
                            msg = email.message_from_bytes(response_part[1])
                            self._process_email(msg)
                
                except Exception as e:
                    logger.error(f"Error processing email {email_id}: {e}")
            
            mail.close()
            mail.logout()
            
            if email_ids:
                logger.info(f"Processed {len(email_ids)} new emails")
        
        except Exception as e:
            logger.error(f"IMAP connection error: {e}")
    
    def _process_email(self, msg):
        subject = self._decode_header(msg.get("Subject", ""))
        sender = msg.get("From", "")
        date = msg.get("Date", "")
        
        logger.info(f"Processing email: {subject} from {sender}")
        
        body = ""
        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() == "text/plain":
                    body = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                    break
        else:
            body = msg.get_payload(decode=True).decode('utf-8', errors='ignore')
        
        if body:
            email_text = f"Email von {sender}\nBetreff: {subject}\nDatum: {date}\n\n{body}"
            self.processor.process_text(email_text, metadata={
                "source": "email",
                "subject": subject,
                "sender": sender,
                "date": date
            })
        
        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_disposition() == 'attachment':
                    filename = part.get_filename()
                    if filename:
                        logger.info(f"Email attachment detected: {filename}")
    
    def _decode_header(self, header):
        if not header:
            return ""
        
        decoded_parts = decode_header(header)
        decoded_string = ""
        
        for part, encoding in decoded_parts:
            if isinstance(part, bytes):
                decoded_string += part.decode(encoding or 'utf-8', errors='ignore')
            else:
                decoded_string += part
        
        return decoded_string
