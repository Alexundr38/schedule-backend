import os
import shutil
import uuid
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Response, Query, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Union
from pathlib import Path

from backend.crud import event_crud, auth_crud
from backend.parser import parse_excel_file
from backend.schemas import event_schema, excel_schema
from backend.database import get_db

router = APIRouter(prefix="/excel", tags=["excel"])

UPLOAD_DIR = Path("temp_uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/upload", response_model=excel_schema.ParsedExcel)
async def upload_excel(
        file: UploadFile = File(...),
        global_group_id: str = Form(...),
        user_id: str = Depends(auth_crud.get_user_id),
        db: AsyncSession = Depends(get_db)
):
    await auth_crud.check_relations(db, global_group_id, user_id)

    if not (file.filename.endswith(('.xlsx', '.xls'))):
        raise HTTPException(
            status_code=400,
            detail="Only Excel or CSV files are allowed"
        )

    suffix = Path(file.filename).suffix
    temp_file_path = UPLOAD_DIR / f"temp_{uuid.uuid4().hex}{suffix}"

    try:
        with open(temp_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        result = parse_excel_file(temp_file_path)

        return result
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
    finally:
        if temp_file_path.exists():
            temp_file_path.unlink()