from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from backend.crud import subject_crud, auth_crud
from backend.schemas import subject_schema
from backend.database import get_db

router = APIRouter(prefix="/subject", tags=["subject"])

@router.get("/list", response_model=List[subject_schema.Subject])
async def get_subject_list(
        global_group_id: str,
        user_id: str = Depends(auth_crud.get_user_id),
        db: AsyncSession = Depends(get_db)) -> List[subject_schema.Subject]:

    await auth_crud.check_relations(db, global_group_id, user_id)

    subjects = await subject_crud.get_subjects_by_global_group(db, global_group_id)
    return subjects


@router.get("/list_name_id", response_model=List[subject_schema.Subject])
async def get_subject_name_id_list(
        global_group_id: str,
        user_id: str = Depends(auth_crud.get_user_id),
        db: AsyncSession = Depends(get_db)) -> List[subject_schema.Subject]:

    await auth_crud.check_relations(db, global_group_id, user_id)

    subjects = await subject_crud.get_subjects_name_id_by_global_group(db, global_group_id)
    return subjects


@router.post("/create", response_model=subject_schema.Subject)
async def create_subject(
        subject: subject_schema.SubjectCreate,
        user_id: str = Depends(auth_crud.get_user_id),
        db: AsyncSession = Depends(get_db)):

    print(subject.name)

    await auth_crud.check_relations(db, subject.global_group_id, user_id) #TODO other check

    db_subject = await subject_crud.add_subject(db, subject.global_group_id, subject.name)
    return db_subject


@router.delete("/delete", status_code=204)
async def delete_subject(
        subject: subject_schema.SubjectGlobalGroup,
        user_id: str = Depends(auth_crud.get_user_id),
        db: AsyncSession = Depends(get_db)):

    await auth_crud.check_relations(db, subject.global_group_id, user_id)

    await subject_crud.delete_subject(db, subject.global_group_id, subject.subject_id)


@router.put("/update", response_model=subject_schema.Subject)
async def update_subject(
        subject: subject_schema.SubjectGlobalGroup,
        user_id: str = Depends(auth_crud.get_user_id),
        db: AsyncSession = Depends(get_db)):

    await auth_crud.check_relations(db, subject.global_group_id, user_id)

    db_subject = await subject_crud.update_subject(db, subject.subject_id, subject.name, subject.global_group_id)
    return db_subject