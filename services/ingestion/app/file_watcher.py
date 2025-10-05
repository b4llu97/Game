import os
import time
import logging
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from document_processor import DocumentProcessor

logger = logging.getLogger(__name__)

class DocumentHandler(FileSystemEventHandler):
    def __init__(self, processor: DocumentProcessor):
        self.processor = processor
        self.processed_files = set()
    
    def on_created(self, event):
        if event.is_directory:
            return
        
        file_path = event.src_path
        
        if file_path in self.processed_files:
            return
        
        time.sleep(1)
        
        if self._is_supported_file(file_path):
            logger.info(f"New file detected: {file_path}")
            try:
                self.processor.process_file(file_path)
                self.processed_files.add(file_path)
            except Exception as e:
                logger.error(f"Error processing {file_path}: {e}")
    
    def _is_supported_file(self, file_path: str) -> bool:
        supported_extensions = {'.pdf', '.docx', '.doc', '.txt', '.png', '.jpg', '.jpeg', '.tiff'}
        return Path(file_path).suffix.lower() in supported_extensions

class FileWatcher:
    def __init__(self, watch_path: str):
        self.watch_path = watch_path
        self.processor = DocumentProcessor()
        self.observer = None
    
    def start(self):
        if not os.path.exists(self.watch_path):
            logger.warning(f"Watch path does not exist: {self.watch_path}")
            logger.info(f"Creating directory: {self.watch_path}")
            os.makedirs(self.watch_path, exist_ok=True)
        
        event_handler = DocumentHandler(self.processor)
        self.observer = Observer()
        self.observer.schedule(event_handler, self.watch_path, recursive=True)
        self.observer.start()
        
        logger.info(f"Watching directory: {self.watch_path}")
        
        try:
            while True:
                time.sleep(10)
        except KeyboardInterrupt:
            self.stop()
    
    def stop(self):
        if self.observer:
            self.observer.stop()
            self.observer.join()
            logger.info("File watcher stopped")
