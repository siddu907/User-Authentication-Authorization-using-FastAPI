from sqlalchemy.orm import Session

import models
import schemas
import utils
from config import settings


def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()


def get_user_by_id(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_all_users(db: Session):
    return db.query(models.User).all()


def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = utils.hash_password(user.password)
    db_user = models.User(
        full_name=user.full_name,
        email=str(user.email),
        hashed_password=hashed_password,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_user_tasks(db: Session, user_id: int):
    return db.query(models.Task).filter(models.Task.user_id == user_id).all()


def get_tasks_by_user_id(db: Session, user_id: int):
    return get_user_tasks(db, user_id)


def get_all_tasks(db: Session):
    return db.query(models.Task).all()


def get_task_by_id(db: Session, task_id: int):
    return db.query(models.Task).filter(models.Task.id == task_id).first()


def create_task(db: Session, task: schemas.TaskCreate, user_id: int):
    db_task = models.Task(**task.model_dump(), user_id=user_id)
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task


def update_task(db: Session, task: models.Task, task_update: schemas.TaskUpdate):
    for field, value in task_update.model_dump(exclude_unset=True).items():
        setattr(task, field, value)
    db.commit()
    db.refresh(task)
    return task


def delete_task(db: Session, task: models.Task):
    db.delete(task)
    db.commit()


def delete_user(db: Session, user: models.User):
    db.delete(user)
    db.commit()
