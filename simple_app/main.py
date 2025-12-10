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

# TTS Testing Endpoint
@app.post("/api/model/{model_id}/test-tts")
async def test_tts(
    model_id: int,
    text: str = Form(...),
    db: Session = Depends(get_db)
):
    """
    Simula la generación de TTS con el modelo.
    En producción, aquí integrarías con RVC/Inference.
    """
    model = db.query(models.Model).filter(models.Model.id == model_id).first()
    if not model:
        raise HTTPException(status_code=404, detail="Modelo no encontrado")
    
    # Simular procesamiento TTS
    # En una implementación real, aquí usarías el modelo .pth y .index
    # con una librería de inferencia de RVC
    
    # Por ahora, creamos un archivo de audio simulado (placeholder)
    output_filename = f"tts_{model_id}_{datetime.now().timestamp()}.txt"
    output_path = AUDIO_DIR / output_filename
    
    # Guardar metadata del audio generado
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(f"Texto: {text}\n")
        f.write(f"Modelo: {model.name}\n")
        f.write(f"Tecnología: {model.technology}\n")
        f.write(f"Epochs: {model.epochs}\n")
        f.write(f"Idioma: {model.language}\n")
        f.write(f"\n[En producción, aquí estaría el audio generado con RVC]\n")
        f.write(f"PTH: {model.pth_file}\n")
        f.write(f"INDEX: {model.index_file}\n")
    
    return {
        "message": "TTS simulado generado (integra RVC para audio real)",
        "model_name": model.name,
        "text": text,
        "info_file": f"/audio/{output_filename}",
        "note": "Para audio real, integra con RVC inference usando los archivos .pth y .index"
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
