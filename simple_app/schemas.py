from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List

class ModelBase(BaseModel):
    created_at: datetime
    name: str
    description: Optional[str] = None
    technology: str = "RVMPE"
    epochs: int
    language: str

class ModelCreate(ModelBase):
    pass

class ModelUpdate(BaseModel):
    created_at: Optional[datetime] = None
    name: Optional[str] = None
    description: Optional[str] = None
    technology: Optional[str] = None
    epochs: Optional[int] = None
    language: Optional[str] = None

class Model(ModelBase):
    id: int
    pth_file: str
    index_file: str
    
    class Config:
        from_attributes = True

class PaginatedModels(BaseModel):
    items: List[Model]
    total: int
    page: int
    per_page: int
    pages: int
