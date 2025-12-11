from fastapi import FastAPI, Request, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from pathlib import Path
from datetime import datetime
import os
import shutil

from simple_app.database import engine, Base, get_db
from simple_app import models, schemas
import edge_tts
import asyncio
import sys

# Ensure the root directory is in sys.path to import rvc
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from rvc.infer.infer import VoiceConverter

# Initialize VoiceConverter
infer_pipeline = VoiceConverter()

# Create database tables
Base.metadata.create_all(bind=engine)

# Create uploads directory
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

# Create audio outputs directory
AUDIO_DIR = Path("audio_outputs")
AUDIO_DIR.mkdir(exist_ok=True)

app = FastAPI(
    title="Voice Models API",
    description="API para gestionar modelos de voz RVC",
    version="1.0.0"
)

# Mount static files for audio
app.mount("/audio", StaticFiles(directory=str(AUDIO_DIR)), name="audio")

# Templates
templates = Jinja2Templates(directory="simple_app/templates")

# API Endpoints
@app.get("/api/model", response_model=schemas.PaginatedModels)
def list_models(
    page: int = 1,
    per_page: int = 10,
    search: str = None,
    db: Session = Depends(get_db)
):
    query = db.query(models.Model)
    
    if search:
        query = query.filter(models.Model.name.contains(search))
    
    total = query.count()
    pages = (total + per_page - 1) // per_page
    
    models_list = query.offset((page - 1) * per_page).limit(per_page).all()
    
    return schemas.PaginatedModels(
        items=[schemas.Model.model_validate(m) for m in models_list],
        total=total,
        page=page,
        per_page=per_page,
        pages=pages
    )

@app.post("/api/model", response_model=schemas.Model, status_code=201)
async def create_model(
    created_at: str = Form(...),
    name: str = Form(...),
    description: str = Form(None),
    pth_file: UploadFile = File(...),
    index_file: UploadFile = File(...),
    technology: str = Form("RVMPE"),
    epochs: int = Form(...),
    language: str = Form(...),
    db: Session = Depends(get_db)
):
    # Validate file extensions
    if not pth_file.filename.endswith('.pth'):
        raise HTTPException(status_code=400, detail="El archivo PTH debe tener extensión .pth")
    if not index_file.filename.endswith('.index'):
        raise HTTPException(status_code=400, detail="El archivo INDEX debe tener extensión .index")
    
    # Parse datetime
    try:
        created_datetime = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
    except:
        raise HTTPException(status_code=400, detail="Formato de fecha inválido. Use ISO 8601")
    
    # Save files
    pth_path = UPLOAD_DIR / f"{datetime.now().timestamp()}_{pth_file.filename}"
    index_path = UPLOAD_DIR / f"{datetime.now().timestamp()}_{index_file.filename}"
    
    with open(pth_path, "wb") as buffer:
        shutil.copyfileobj(pth_file.file, buffer)
    
    with open(index_path, "wb") as buffer:
        shutil.copyfileobj(index_file.file, buffer)
    
    # Create model in database
    db_model = models.Model(
        created_at=created_datetime,
        name=name,
        description=description,
        pth_file=str(pth_path),
        index_file=str(index_path),
        technology=technology,
        epochs=epochs,
        language=language
    )
    
    db.add(db_model)
    db.commit()
    db.refresh(db_model)
    
    return schemas.Model.model_validate(db_model)

@app.get("/api/model/{model_id}", response_model=schemas.Model)
def get_model(model_id: int, db: Session = Depends(get_db)):
    model = db.query(models.Model).filter(models.Model.id == model_id).first()
    if not model:
        raise HTTPException(status_code=404, detail="Modelo no encontrado")
    return schemas.Model.model_validate(model)

@app.put("/api/model/{model_id}", response_model=schemas.Model)
async def update_model(
    model_id: int,
    created_at: str = Form(None),
    name: str = Form(None),
    description: str = Form(None),
    pth_file: UploadFile = File(None),
    index_file: UploadFile = File(None),
    technology: str = Form(None),
    epochs: int = Form(None),
    language: str = Form(None),
    db: Session = Depends(get_db)
):
    model = db.query(models.Model).filter(models.Model.id == model_id).first()
    if not model:
        raise HTTPException(status_code=404, detail="Modelo no encontrado")
    
    if created_at:
        try:
            model.created_at = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
        except:
            raise HTTPException(status_code=400, detail="Formato de fecha inválido")
    
    if name:
        model.name = name
    if description is not None:
        model.description = description
    if technology:
        model.technology = technology
    if epochs:
        model.epochs = epochs
    if language:
        model.language = language
    
    if pth_file:
        if not pth_file.filename.endswith('.pth'):
            raise HTTPException(status_code=400, detail="El archivo PTH debe tener extensión .pth")
        
        # Delete old file
        if os.path.exists(model.pth_file):
            os.remove(model.pth_file)
        
        # Save new file
        pth_path = UPLOAD_DIR / f"{datetime.now().timestamp()}_{pth_file.filename}"
        with open(pth_path, "wb") as buffer:
            shutil.copyfileobj(pth_file.file, buffer)
        model.pth_file = str(pth_path)
    
    if index_file:
        if not index_file.filename.endswith('.index'):
            raise HTTPException(status_code=400, detail="El archivo INDEX debe tener extensión .index")
        
        # Delete old file
        if os.path.exists(model.index_file):
            os.remove(model.index_file)
        
        # Save new file
        index_path = UPLOAD_DIR / f"{datetime.now().timestamp()}_{index_file.filename}"
        with open(index_path, "wb") as buffer:
            shutil.copyfileobj(index_file.file, buffer)
        model.index_file = str(index_path)
    
    db.commit()
    db.refresh(model)
    
    return schemas.Model.model_validate(model)

@app.delete("/api/model/{model_id}", status_code=204)
def delete_model(model_id: int, db: Session = Depends(get_db)):
    model = db.query(models.Model).filter(models.Model.id == model_id).first()
    if not model:
        raise HTTPException(status_code=404, detail="Modelo no encontrado")
    
    # Delete files
    if os.path.exists(model.pth_file):
        os.remove(model.pth_file)
    if os.path.exists(model.index_file):
        os.remove(model.index_file)
    
    db.delete(model)
    db.commit()
    
    return None

@app.get("/api/model/{model_id}/download/{file_type}")
def download_file(model_id: int, file_type: str, db: Session = Depends(get_db)):
    model = db.query(models.Model).filter(models.Model.id == model_id).first()
    if not model:
        raise HTTPException(status_code=404, detail="Modelo no encontrado")
    
    if file_type == "pth":
        file_path = model.pth_file
        filename = f"{model.name}.pth"
    elif file_type == "index":
        file_path = model.index_file
        filename = f"{model.name}.index"
    else:
        raise HTTPException(status_code=400, detail="Tipo de archivo inválido. Use 'pth' o 'index'")
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Archivo no encontrado")
    
    return FileResponse(
        path=file_path,
        filename=filename,
        media_type="application/octet-stream"
    )

@app.get("/api/tts-voices")
async def get_tts_voices():
    """
    Lista las voces disponibles para TTS (Edge-TTS).
    Filtra solo voces en Español e Inglés.
    """
    all_voices = await edge_tts.list_voices()
    
    # Filter for English (en-) and Spanish (es-)
    # Exclude voices known to be problematic if necessary, though usually list_voices returns available ones.
    filtered_voices = [
        v for v in all_voices 
        if (v['Locale'].startswith('en-') or v['Locale'].startswith('es-'))
    ]
    
    return sorted(filtered_voices, key=lambda x: x['ShortName'])

# TTS Testing Endpoint
@app.post("/api/model/{model_id}/test-tts")
async def test_tts(
    model_id: int,
    text: str = Form(...),
    tts_voice: str = Form("en-US-AriaNeural"),
    pitch: int = Form(0),
    db: Session = Depends(get_db)
):
    """
    Genera audio TTS y luego aplica RVC.
    """
    print(f"DEBUG: test_tts called with text='{text}', tts_voice='{tts_voice}', pitch={pitch}")
    
    model = db.query(models.Model).filter(models.Model.id == model_id).first()
    if not model:
        raise HTTPException(status_code=404, detail="Modelo no encontrado")
    
    # 1. Generate TTS
    timestamp = datetime.now().timestamp()
    tts_filename = f"tts_raw_{model_id}_{timestamp}.wav"
    tts_path = AUDIO_DIR / tts_filename
    
    communicate = edge_tts.Communicate(text, tts_voice)
    try:
        await communicate.save(str(tts_path))
    except Exception as e:
        print(f"ERROR in edge_tts: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Error generando TTS con voz '{tts_voice}': {str(e)}")
    
    # 2. Apply RVC
    output_filename = f"rvc_out_{model_id}_{timestamp}.wav"
    output_path = AUDIO_DIR / output_filename
    
    # Ensure paths are absolute strings for RVC
    pth_path = str(Path(model.pth_file).absolute())
    index_path = str(Path(model.index_file).absolute())
    input_path_str = str(tts_path.absolute())
    output_path_str = str(output_path.absolute())
    
    try:
        # Run inference in a separate thread to not block the event loop
        # Since convert_audio is synchronous and might be heavy
        await asyncio.to_thread(
            infer_pipeline.convert_audio,
            audio_input_path=input_path_str,
            audio_output_path=output_path_str,
            model_path=pth_path,
            index_path=index_path,
            sid=0,
            pitch=pitch
        )
    except Exception as e:
        # Cleanup on error
        if tts_path.exists():
            os.remove(tts_path)
        raise HTTPException(status_code=500, detail=f"Error en inferencia RVC: {str(e)}")

    return {
        "message": "Audio generado exitosamente",
        "model_name": model.name,
        "text": text,
        "tts_voice": tts_voice,
        "info_file": f"/audio/{output_filename}",
        "raw_tts_file": f"/audio/{tts_filename}"
    }

# Frontend
@app.get("/")
async def home(request: Request, page: int = 1, search: str = None, db: Session = Depends(get_db)):
    query = db.query(models.Model)
    
    if search:
        query = query.filter(models.Model.name.contains(search))
    
    total = query.count()
    per_page = 10
    pages = (total + per_page - 1) // per_page
    
    models_list = query.offset((page - 1) * per_page).limit(per_page).all()
    
    return templates.TemplateResponse("index.html", {
        "request": request,
        "models": models_list,
        "page": page,
        "pages": pages,
        "search": search or ""
    })

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
