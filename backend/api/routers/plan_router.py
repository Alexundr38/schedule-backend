from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from backend.crud import auth_crud, plan_crud
from backend.schemas import plan_schema
from backend.database import get_db

router = APIRouter(prefix="/plan", tags=["Plan"])

@router.post("/create", response_model=List[plan_schema.Plan])
async def create_plan(
        plans: List[plan_schema.PlanBase],
        user_id: str = Depends(auth_crud.get_user_id),
        db: AsyncSession = Depends(get_db)):

    await auth_crud.check_relations(db, plans[0].global_group_id, user_id)

    db_plan = plan_crud.add_plan(db, plans)
    return db_plan

@router.get("/list", response_model=List[plan_schema.PlanAllData])
async def get_plan_list(
        global_group_id: str,
        user_id: str = Depends(auth_crud.get_user_id),
        db: AsyncSession = Depends(get_db)):

    await auth_crud.check_relations(db, global_group_id, user_id)

    db_plans = await plan_crud.get_plans_by_global_group(db, global_group_id)
    return db_plans