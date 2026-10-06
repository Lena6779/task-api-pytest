from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import Base, engine, get_db

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Task CRUD API")

@app.post("/tasks", response_model=schemas.TaskResponse, status_code=201)
def create_task(task: schemas.TaskCreate, db: Session = Depends(get_db)):
    """Create a new task. Titles must be unique."""
    # Reject duplicates with 409 Conflict before touching the database
    existing = db.query(models.Task).filter(models.Task.title == task.title).first()
    if existing:
        raise HTTPException(status_code=409, detail="A task with this title already exists")

    db_task = models.Task(**task.model_dump())
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task


@app.get("/tasks", response_model=list[schemas.TaskResponse])
def list_tasks(db: Session = Depends(get_db)):
    return db.query(models.Task).all()


@app.get("/tasks/{task_id}", response_model=schemas.TaskResponse)
def get_task(task_id: int, db: Session = Depends(get_db)):
    task = db.get(models.Task, task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@app.patch("/tasks/{task_id}", response_model=schemas.TaskResponse)
def update_task(task_id: int, updates: schemas.TaskUpdate, db: Session = Depends(get_db)):
    """Partially update a task. Only fields included in the request are changed."""
    task = db.get(models.Task, task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
         # exclude_unset=True skips fields the client didn't send,
        # so omitted fields aren't overwritten with None
    for field, value in updates.model_dump(exclude_unset=True).items():
        setattr(task, field, value)
    db.commit()
    db.refresh(task)
    return task


@app.delete("/tasks/{task_id}", status_code=204)
def delete_task(task_id: int, db: Session = Depends(get_db)):
    task = db.get(models.Task, task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    db.delete(task)
    db.commit()