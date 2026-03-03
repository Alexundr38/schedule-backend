from typing import List, Optional

from fastapi import HTTPException
from sqlalchemy.engine import Row

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from backend.models import models
from backend.models.models import EventFormat
from backend.schemas import plan_schema

async def get_plan_by_all_parameters(db: AsyncSession, plan_data: plan_schema.PlanBase) -> Optional[Row]:

    db_plan = await db.execute(
        select(
            models.Plan,
            models.TeacherPlan.teacher_id,
            models.TeacherPlan.priority,
        ).\
        join(models.TeacherPlan).\
        where(
            models.Plan.global_group_id == plan_data.global_group_id,
            models.Plan.group_id == plan_data.group_id,
            models.Plan.subject_id == plan_data.subject_id,
            models.Plan.event_id == plan_data.event_id,
            models.Plan.event_format == EventFormat(plan_data.event_format),
            models.Plan.hours == plan_data.hours,
            models.TeacherPlan.teacher_id == plan_data.teacher_id,
            models.TeacherPlan.priority == plan_data.priority,
        )
    )

    return db_plan.one_or_none()


async def add_plan(db: AsyncSession, plan_data: List[plan_schema.PlanBase]) -> List[plan_schema.PlanAllData]:
    try:
        db_plans_id = []
        #check for prinadlejnost

        for plan in plan_data:

            #check plan in db
            check_plan = await get_plan_by_all_parameters(db, plan)
            if check_plan:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Plan already exists for group {plan.group_id}, subject {plan.subject_id}," +
                           f"teacher {plan.teacher_id}, event {plan.event_id}, priority {plan.priority}"
                )

            db_plan = models.Plan(
                global_group_id=plan.global_group_id,
                group_id=plan.group_id,
                subject_id=plan.subject_id,
                event_id=plan.event_id,
                event_format=EventFormat(plan.event_format),
                hours=plan.hours,
            )

            db.add(db_plan)
            await db.flush()
            await db.refresh(db_plan)

            db_teacher_plan = models.TeacherPlan(
                plan_id=db_plan.plan_id,
                teacher_id=plan.teacher_id,
                priority=plan.priority,
            )

            db.add(db_teacher_plan)
            db_plans_id.append(db_plan.plan_id)

        await db.commit()

        db_plans = []
        for plan_id in db_plans_id:
            db_plans.append(await get_plan_by_plan_id(db, plan_id))
        return db_plans

    except (HTTPException) as e:
        await db.rollback()
        raise e


async def get_plan_by_plan_id(db: AsyncSession, plan_id: str) -> plan_schema.PlanAllData:

    response = (await db.execute(
        select(
            models.Plan,
            models.Group.name.label('group_name'),
            models.Subject.name.label('subject_name'),
            models.Event.name.label('event_name'),
            models.Teacher.name.label('teacher_name'),
            models.TeacherPlan.teacher_id,
            models.TeacherPlan.priority,
        ).\
        join(models.Group).\
        join(models.Subject).\
        join(models.Event).\
        join(models.TeacherPlan).\
        join(models.Teacher).\
        where(
            models.Plan.plan_id == plan_id
        )
    )).mappings().first()

    return plan_schema.PlanAllData(
        global_group_id=response["Plan"].global_group_id,
        plan_id=response["Plan"].plan_id,
        group_id=response["Plan"].group_id,
        group_name=response["group_name"],
        subject_id=response["Plan"].subject_id,
        subject_name=response["subject_name"],
        event_id=response["Plan"].event_id,
        event_name=response["event_name"],
        teacher_id=response["teacher_id"],
        teacher_name=response["teacher_name"],
        priority=response["priority"],
        event_format=response["Plan"].event_format,
        hours=response["Plan"].hours
    )


async def get_plans_by_global_group(db: AsyncSession, global_group_id: str) -> List[plan_schema.PlanAllData]:

    response = (await db.execute(
        select(
            models.Plan,
            models.Group.name.label('group_name'),
            models.Subject.name.label('subject_name'),
            models.Event.name.label('event_name'),
            models.Teacher.name.label('teacher_name'),
            models.TeacherPlan.teacher_id,
            models.TeacherPlan.priority,
        ).\
        join(models.Group).\
        join(models.Subject).\
        join(models.Event).\
        join(models.TeacherPlan).\
        join(models.Teacher).\
        where(
            models.Plan.global_group_id == global_group_id
        )
    )).mappings().all()

    return [plan_schema.PlanAllData(
        global_group_id=row["Plan"].global_group_id,
        plan_id=row["Plan"].plan_id,
        group_id=row["Plan"].group_id,
        group_name=row["group_name"],
        subject_id=row["Plan"].subject_id,
        subject_name=row["subject_name"],
        event_id=row["Plan"].event_id,
        event_name=row["event_name"],
        teacher_id=row["teacher_id"],
        teacher_name=row["teacher_name"],
        priority=row["priority"],
        event_format=row["Plan"].event_format,
        hours=row["Plan"].hours
    ) for row in response]


async def delete_plan(db: AsyncSession, plan_data: plan_schema.PlanGlobalGroup):
    result = await db.execute (
        delete(models.Plan).\
        where(
            models.Plan.plan_id == plan_data.plan_id,
            models.Plan.global_group_id == plan_data.global_group_id,   #TODO mb delete
        )
    )

    if result.rowcount == 0:
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail="Plan does not exist"
        )

    await db.commit()


async def update_plan(db: AsyncSession, plan_data: plan_schema.Plan) -> plan_schema.PlanAllData:
    db_plan = (await db.execute(
        select(
            models.Plan.group_id,
            models.Plan.subject_id,
            models.Plan.event_id,
            models.Plan.event_format,
            models.Plan.hours,
            models.TeacherPlan.teacher_id
        ).
        join(models.TeacherPlan).
        where(
            models.TeacherPlan.teacher_id == plan_data.teacher_id,
            models.Plan.subject_id == plan_data.subject_id,
            models.Plan.event_id == plan_data.event_id,
            models.Plan.event_format == plan_data.event_format,
            models.Plan.hours == plan_data.hours,
            models.Plan.group_id == plan_data.group_id,
        )
    )).first()

    if db_plan:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Plan already exists"
        )

    plan = (await db.execute(
        select(models.Plan).
        where(models.Plan.plan_id == plan_data.plan_id)
    )).scalar()

    teacher_plan = (await db.execute(
        select(models.TeacherPlan).
        where(models.TeacherPlan.plan_id == plan_data.plan_id)
    )).scalar()

    if str(teacher_plan.teacher_id) != plan_data.teacher_id:
        await db.delete(teacher_plan)

        new_teacher_plan = models.TeacherPlan(
            plan_id=plan_data.plan_id,
            teacher_id=plan_data.teacher_id,
        )

        db.add(new_teacher_plan)
        await db.flush()
        plan.teacher_id = plan_data.teacher_id

    if str(plan.group_id) != plan_data.group_id:
        plan.group_id = plan_data.group_id

    if str(plan.subject_id) != plan_data.subject_id:
        plan.subject_id = plan_data.subject_id

    if str(plan.event_id) != plan_data.event_id:
        plan.event_id = plan_data.event_id

    if str(plan.event_format) != plan_data.event_format:
        plan.event_format = EventFormat(plan_data.event_format)

    if plan.hours != plan_data.hours:
        plan.hours = plan_data.hours

    await db.commit()
    response = await get_plan_by_plan_id(db, plan.plan_id)
    return response


async def get_plans_by_group(db: AsyncSession, plan_data: plan_schema.PlanGroup) -> List[plan_schema.PlanAllData]:

    response = (await db.execute(
        select(
            models.Plan,
            models.Group.name.label('group_name'),
            models.Subject.name.label('subject_name'),
            models.Event.name.label('event_name'),
            models.Teacher.name.label('teacher_name'),
            models.TeacherPlan.teacher_id,
            models.TeacherPlan.priority,
        ).
        join(models.Group).
        join(models.Subject).
        join(models.Event).
        join(models.TeacherPlan).
        join(models.Teacher).
        where(
            models.Plan.global_group_id == plan_data.global_group_id,
            models.Plan.group_id == plan_data.group_id,
        )
    )).mappings().all()

    return [plan_schema.PlanAllData(
        global_group_id=row["Plan"].global_group_id,
        plan_id=row["Plan"].plan_id,
        group_id=row["Plan"].group_id,
        group_name=row["group_name"],
        subject_id=row["Plan"].subject_id,
        subject_name=row["subject_name"],
        event_id=row["Plan"].event_id,
        event_name=row["event_name"],
        teacher_id=row["teacher_id"],
        teacher_name=row["teacher_name"],
        priority=row["priority"],
        event_format=row["Plan"].event_format,
        hours=row["Plan"].hours
    ) for row in response]