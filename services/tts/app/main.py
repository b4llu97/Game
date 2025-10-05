from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
import subprocess
import tempfile
import os
import uuid

app = FastAPI(title="Jarvis TTS Service", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

PIPER_MODEL = "/app/models/de_DE-thorsten-medium.onnx"
OUTPUT_DIR = "/app/output"

class SpeakRequest(BaseModel):
    text: str
    speed: float = 1.0

@app.get("/")
def root():
    return {"service": "Jarvis TTS", "status": "running"}

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "model": "de_DE-thorsten-medium",
        "voice": "thorsten"
    }

@app.post("/v1/speak")
async def speak_text(request: SpeakRequest):
    if not request.text or len(request.text.strip()) == 0:
        raise HTTPException(status_code=400, detail="Kein Text angegeben")
    
    audio_id = str(uuid.uuid4())
    output_file = os.path.join(OUTPUT_DIR, f"{audio_id}.wav")
    
    try:
        cmd = [
            "piper",
            "--model", PIPER_MODEL,
            "--output_file", output_file,
            "--length_scale", str(1.0 / request.speed)
        ]
        
        process = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        stdout, stderr = process.communicate(input=request.text)
        
        if process.returncode != 0:
            raise Exception(f"Piper TTS error: {stderr}")
        
        if not os.path.exists(output_file):
            raise Exception("Audio-Datei wurde nicht erstellt")
        
        return FileResponse(
            output_file,
            media_type="audio/wav",
            filename=f"speech_{audio_id}.wav",
            background=None
        )
    
    except Exception as e:
        if os.path.exists(output_file):
            os.remove(output_file)
        raise HTTPException(status_code=500, detail=f"Fehler bei der Sprachsynthese: {str(e)}")
