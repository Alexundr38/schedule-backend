from sqlalchemy.orm import DeclarativeBase, relationship
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy import Column, Integer, String, ForeignKey, UUID, DateTime, Time, Date
from sqlalchemy.schema import MetaData
import uuid
from sqlalchemy import Enum as SQLAlchemyEnum
import enum

metadata = MetaData(schema="schedule_schema")

class Base(AsyncAttrs, DeclarativeBase):
    metadata = metadata


class EventFormat(enum.Enum):
    ONLINE = "ONLINE"
    OFFLINE = "OFFLINE"


class User(Base):
    __tablename__ = "user"

    user_id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    name = Column(
        String(255),
        nullable=False
    )
    email = Column(
        String(255),
        nullable=False,
        unique=True
    )
    password = Column(
        String(60),
        nullable=False
    )
    date_registration = Column(DateTime)

    global_group_associations = relationship(
        "GlobalGroupUser",
        back_populates="user"
    )


class GlobalGroup(Base):
    __tablename__ = "global_group"

    global_group_id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    name = Column(String(255))

    user_associations = relationship(
        "GlobalGroupUser",
        back_populates="global_group"
    )
    subject_associations = relationship(
        "GlobalGroupSubject",
        back_populates="global_group"
    )
    group_associations = relationship(
        "GlobalGroupGroup",
        back_populates="global_group"
    )
    event_associations = relationship(
        "GlobalGroupEvent",
        back_populates="global_group"
    )
    teacher_associations = relationship(
        "GlobalGroupTeacher",
        back_populates="global_group"
    )
    time_group_associations = relationship(
        "GlobalGroupTimeGroup",
        back_populates="global_group"
    )
    plan = relationship(
        "Plan",
        back_populates="global_group"
    )


class GlobalGroupUser(Base):
    __tablename__ = "global_group_user"

    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("user.user_id", ondelete="CASCADE"),
        primary_key=True
    )

    global_group_id = Column(
        UUID(as_uuid=True),
        ForeignKey("global_group.global_group_id", ondelete="CASCADE"),
        primary_key=True
    )

    user = relationship(
        "User",
        back_populates="global_group_associations"
    )
    global_group = relationship(
        "GlobalGroup",
        back_populates="user_associations"
    )


class Subject(Base):
    __tablename__ = "subject"

    subject_id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    name = Column(String(255))
    #hours = Column(Integer)

    global_group_associations = relationship(
        "GlobalGroupSubject",
        back_populates="subject"
    )

    plans = relationship(
        "Plan",
        back_populates="subject"
    )


class GlobalGroupSubject(Base):
    __tablename__ = "global_group_subject"

    subject_id = Column(
        UUID(as_uuid=True),
        ForeignKey("subject.subject_id", ondelete="CASCADE"),
        primary_key=True
    )
    global_group_id = Column(
        UUID(as_uuid=True),
        ForeignKey("global_group.global_group_id", ondelete="CASCADE"),
        primary_key=True
    )

    subject = relationship(
        "Subject",
        back_populates="global_group_associations"
    )
    global_group = relationship(
        "GlobalGroup",
        back_populates="subject_associations"
    )


class Group(Base):
    __tablename__ = "group"

    group_id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    name = Column(String(255))

    student_count = Column(Integer, default=0)

    global_group_associations = relationship(
        "GlobalGroupGroup",
        back_populates="group"
    )

    plans = relationship(
        "Plan",
        back_populates="group"
    )

class GlobalGroupGroup(Base):
    __tablename__ = "global_group_group"

    group_id = Column(
        UUID(as_uuid=True),
        ForeignKey("group.group_id", ondelete="CASCADE"),
        primary_key=True
    )
    global_group_id = Column(
        UUID(as_uuid=True),
        ForeignKey("global_group.global_group_id", ondelete="CASCADE"),
        primary_key=True
    )

    group = relationship(
        "Group",
        back_populates="global_group_associations"
    )
    global_group = relationship(
        "GlobalGroup",
        back_populates="group_associations"
    )


class Event(Base):
    __tablename__ = "event"

    event_id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    name = Column(String(255))

    global_group_associations = relationship(
        "GlobalGroupEvent",
        back_populates="event"
    )

    plans = relationship(
        "Plan",
        back_populates="event"
    )


class GlobalGroupEvent(Base):
    __tablename__ = "global_group_event"

    event_id = Column(
        UUID(as_uuid=True),
        ForeignKey("event.event_id", ondelete="CASCADE"),
        primary_key=True
    )
    global_group_id = Column(
        UUID(as_uuid=True),
        ForeignKey("global_group.global_group_id", ondelete="CASCADE"),
        primary_key=True
    )

    event = relationship(
        "Event",
        back_populates="global_group_associations"
    )
    global_group = relationship(
        "GlobalGroup",
        back_populates="event_associations"
    )


class Teacher(Base):
    __tablename__ = "teacher"

    teacher_id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    name = Column(String(255))

    global_group_associations = relationship(
        "GlobalGroupTeacher",
        back_populates="teacher"
    )
    lesson_associations = relationship(
        "TeacherLesson",
        back_populates="teacher"
    )
    plan_associations = relationship(
        "TeacherPlan",
        back_populates="teacher"
    )


class GlobalGroupTeacher(Base):
    __tablename__ = "global_group_teacher"

    teacher_id = Column(
        UUID(as_uuid=True),
        ForeignKey("teacher.teacher_id", ondelete="CASCADE"),
        primary_key=True
    )
    global_group_id = Column(
        UUID(as_uuid=True),
        ForeignKey("global_group.global_group_id", ondelete="CASCADE"),
        primary_key=True
    )

    teacher = relationship(
        "Teacher",
        back_populates="global_group_associations"
    )
    global_group = relationship(
        "GlobalGroup",
        back_populates="teacher_associations"
    )


class Plan(Base):
    __tablename__ = "plan"

    plan_id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    global_group_id = Column(
        UUID(as_uuid=True),
        ForeignKey("global_group.global_group_id", ondelete="CASCADE"),
        nullable=False
    )
    subject_id = Column(
        UUID(as_uuid=True),
        ForeignKey("subject.subject_id", ondelete="CASCADE"),
        nullable=False
    )
    group_id = Column(
        UUID(as_uuid=True),
        ForeignKey("group.group_id", ondelete="CASCADE"),
        nullable=False
    )
    event_id = Column(
        UUID(as_uuid=True),
        ForeignKey("event.event_id", ondelete="CASCADE"),
        nullable=False
    )
    event_format = Column(
        SQLAlchemyEnum(EventFormat, name="event_format_enum", schema="schedule_schema"),
        default=EventFormat.OFFLINE
    )
    hours = Column(Integer, default=0)

    subject = relationship(
        "Subject",
        back_populates="plans"
    )
    group = relationship(
        "Group",
        back_populates="plans"
    )
    event = relationship(
        "Event",
        back_populates="plans"
    )
    lessons = relationship(
        "Lesson",
        back_populates="plan"
    )
    global_group = relationship(
        "GlobalGroup",
        back_populates="plan"
    )

    teacher_associations = relationship(
        "TeacherPlan",
        back_populates="plan"
    )


class TeacherPlan(Base):
    __tablename__ = "teacher_plan"

    plan_id = Column(
        UUID(as_uuid=True),
        ForeignKey("plan.plan_id", ondelete="CASCADE"),
        primary_key=True,
    )

    teacher_id = Column(
        UUID(as_uuid=True),
        ForeignKey("teacher.teacher_id", ondelete="CASCADE"),
        primary_key=True
    )

    priority = Column(Integer, default=0)

    plan = relationship(
        "Plan",
        back_populates="teacher_associations"
    )

    teacher = relationship(
        "Teacher",
        back_populates="plan_associations"
    )




class TimeGroup(Base):
    __tablename__ = "time_group"

    time_group_id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    name = Column(String(255))

    global_group_associations = relationship(
        "GlobalGroupTimeGroup",
        back_populates="time_group"
    )
    lesson_times = relationship(
        "LessonTime",
        back_populates="time_group"
    )


class GlobalGroupTimeGroup(Base):
    __tablename__ = "global_group_time_group"

    time_group_id = Column(
        UUID(as_uuid=True),
        ForeignKey("time_group.time_group_id", ondelete="CASCADE"),
        primary_key=True
    )
    global_group_id = Column(
        UUID(as_uuid=True),
        ForeignKey("global_group.global_group_id", ondelete="CASCADE"),
        primary_key=True
    )

    time_group = relationship(
        "TimeGroup",
        back_populates="global_group_associations"
    )
    global_group = relationship(
        "GlobalGroup",
        back_populates="time_group_associations"
    )


class LessonTime(Base):
    __tablename__ = "lesson_time"

    lesson_time_id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    time_group_id = Column(
        UUID(as_uuid=True),
        ForeignKey("time_group.time_group_id", ondelete="CASCADE"),
        nullable=False
    )
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)

    time_group = relationship(
        "TimeGroup",
        back_populates="lesson_times"
    )
    lessons = relationship(
        "Lesson",
        back_populates="lesson_time"
    )


class Lesson(Base):
    __tablename__ = "lesson"

    lesson_id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    lesson_time_id = Column(
        UUID(as_uuid=True),
        ForeignKey("lesson_time.lesson_time_id", ondelete="CASCADE"),
        nullable=False
    )
    plan_id = Column(
        UUID(as_uuid=True),
        ForeignKey("plan.plan_id", ondelete="CASCADE"),
        nullable=False
    )

    date = Column(Date, nullable=False)

    lesson_time = relationship(
        "LessonTime",
        back_populates="lessons"
    )
    plan = relationship(
        "Plan",
        back_populates="lessons"
    )

    teacher_associations = relationship(
        "TeacherLesson",
        back_populates="lessons"
    )


class TeacherLesson(Base):
    __tablename__ = "teacher_lesson"

    teacher_id = Column(
        UUID(as_uuid=True),
        ForeignKey("teacher.teacher_id", ondelete="CASCADE"),
        primary_key=True
    )
    lesson_id = Column(
        UUID(as_uuid=True),
        ForeignKey("lesson.lesson_id", ondelete="CASCADE"),
        primary_key=True
    )

    teacher = relationship(
        "Teacher",
        back_populates="lesson_associations"
    )
    lessons = relationship(
        "Lesson",
        back_populates="teacher_associations"
    )