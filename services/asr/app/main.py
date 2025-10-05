from fastapi import FastAPI, File, UploadFile, HTTPException
from faster_whisper import WhisperModel
import tempfile
import os
from pydantic import BaseModel
from typing import Optional

app = FastAPI(title="Jarvis ASR Service", version="1.0.0")

print("Loading Whisper model...")
model = WhisperModel("small", device="cpu", compute_type="int8")
print("Whisper model loaded successfully")

class TranscriptionResponse(BaseModel):
    text: str
    language: str
    duration: Optional[float] = None

@app.get("/")
def root():
    return {"service": "Jarvis ASR", "status": "running"}

@app.get("/health")
def health_check():
    return {"status": "healthy", "model": "faster-whisper-small"}

@app.post("/v1/transcribe", response_model=TranscriptionResponse)
async def transcribe_audio(file: UploadFile = File(...)):
    if not file:
        raise HTTPException(status_code=400, detail="Keine Datei hochgeladen")
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as temp_file:
        content = await file.read()
        temp_file.write(content)
        temp_file_path = temp_file.name
    
    try:
        segments, info = model.transcribe(
            temp_file_path,
            language="de",
            beam_size=5,
            vad_filter=True
        )
        
        full_text = " ".join([segment.text for segment in segments])
        
        return TranscriptionResponse(
            text=full_text.strip(),
            language=info.language,
            duration=info.duration
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Fehler bei der Transkription: {str(e)}")
    
    finally:
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
