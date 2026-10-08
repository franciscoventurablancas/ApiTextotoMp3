from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
import edge_tts
import os
import uuid

app = FastAPI(
    title="API de Texto a Voz",
    description="Genera audios realistas utilizando edge-tts",
    version="1.0"
)

class AudioRequest(BaseModel):
    text: str
    voice: str = "es-MX-DaliaNeural"
    speed: str = "+50%"

def eliminar_archivo(path: str):
    if os.path.exists(path):
        os.remove(path)

@app.post("/generate-audio/")
async def generate_audio(request: AudioRequest, background_tasks: BackgroundTasks):
    if not request.text.strip():
        raise HTTPException(status_code=400, detail="El texto no puede estar vacío.")

    filename = f"audio_{uuid.uuid4()}.mp3"
    
    try:
        communicate = edge_tts.Communicate(request.text, voice=request.voice, rate=request.speed)
        await communicate.save(filename)
        
        background_tasks.add_task(eliminar_archivo, filename)
        
        return FileResponse(
            path=filename,
            media_type="audio/mpeg",
            filename="audio_generado.mp3"
        )
    
    except Exception as e:
        if os.path.exists(filename):
            os.remove(filename)
        raise HTTPException(status_code=500, detail=str(e))
      
