from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

import crud
import models
import oauth2
import schemas
from database import get_db

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/users", response_model=list[schemas.UserDetailResponse])
def list_users(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(oauth2.get_current_admin),
):
    users = crud.get_all_users(db)
    user_responses = []
    for user in users:
        tasks = [task for task in user.tasks]
        user_responses.append(
            schemas.UserDetailResponse(
                id=user.id,
                full_name=user.full_name,
                email=user.email,
                created_at=user.created_at,
                tasks=tasks,
            )
        )
    return user_responses


@router.delete("/users/{user_id}", response_model=schemas.UserDeleteResponse)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(oauth2.get_current_admin),
):
    user = crud.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    crud.delete_user(db, user)
    return {"message": "User deleted successfully"}


@router.get("/tasks", response_model=list[schemas.TaskResponse])
def list_all_tasks(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(oauth2.get_current_admin),
):
    return crud.get_all_tasks(db)


@router.put("/tasks/{task_id}", response_model=schemas.TaskResponse)
def update_any_task(
    task_id: int,
    task_update: schemas.TaskUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(oauth2.get_current_admin),
):
    task = crud.get_task_by_id(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return crud.update_task(db, task, task_update)


@router.delete("/tasks/{task_id}", response_model=schemas.TaskDeleteResponse)
def delete_any_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(oauth2.get_current_admin),
):
    task = crud.get_task_by_id(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    crud.delete_task(db, task)
    return {"message": "Task deleted successfully"}
