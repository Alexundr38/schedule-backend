from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models import models
from backend.schemas import plan_schema


async def add_plan(db: AsyncSession, plan_data: List[plan_schema.PlanCreate]) -> List[plan_schema.Plan]:

    #check for prinadlejnost

    db_plans = []
    for plan in plan_data:
        db_plan = models.Plan(
            group_id=plan.group_id,
            subject_id=plan.subject_id,
            event_id=plan.event_id,
            event_format=plan.event_format,
            hours=plan.hours,
        )

        db.add(db_plan)
        await db.commit()
        await db.refresh(db_plan)

        db_teacher_plan = models.TeacherPlan(
            plan_id=db_plan.plan_id,
            teacher_id=plan.teacher_id,
            priority=plan.priority,
        )

        db.add(db_teacher_plan)
        await db.commit()

        db_plans.append(plan_schema.Plan(
            plan_id=db_plan.plan_id,
            group_id=db_plan.group_id,
            subject_id=db_plan.subject_id,
            event_id=db_plan.event_id,
            teacher_id=db_teacher_plan.teacher_id,
            priority=db_teacher_plan.priority,
            event_format=db_plan.event_format,
            hours=db_plan.hours
        ))

    return db_plans


async def get_plans_by_global_group(db: AsyncSession, global_group_id: str) -> List[plan_schema.PlanAllData]:

    response = await db.execute(
        select(
            models.Plan,
            models.Group.name,
            models.Subject.name,
            models.Event.name,
            models.Teacher.name,
            models.TeacherPlan.priority,
        ).\
        join(
            models.Group,
            models.Subject,
            models.Event,
            models.TeacherPlan,
            models.Teacher
        ).\
        where(
            models.Plan.global_group_id == global_group_id
        )
    ).all()

    return [plan_schema.PlanAllData(
        global_group_id=elem.global_group_id,
        plan_id=elem.plan_id,
        group_id=elem.group_id,
        group_name=elem.group_name,
        subject_id=elem.subject_id,
        subject_name=elem.subject_name,
        event_id=elem.event_id,
        event_name=elem.event_name,
        teacher_id=elem.teacher_id,
        teacher_name=elem.teacher_name,
        priority=elem.priority,
        event_format=elem.event_format,
        hours=elem.hours

    ) for elem in response]