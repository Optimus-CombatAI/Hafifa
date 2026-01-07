from fastapi import APIRouter,File,UploadFile,Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db

router = APIRouter()

@router.post("/upload")
async def upload_csv(file:UploadFile = File(...), db:AsyncSession = Depends(get_db))->dict:
    content = await file.read()
    size_bytes = len(content)
    
    return{
        "filename":file.filename,
        "content_type":file.content_type,
        "size_bytes":size_bytes,
        "db":"ok"
    }

    
    
