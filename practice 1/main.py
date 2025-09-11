from fastapi import FastAPI, HTTPException
from model import Task
from db import get_connection
from mysql.connector import Error

app = FastAPI()

@app.get("/")
def root():
    return {"message": "Welcome to the Task API! Visit /docs to explore the endpoints."}


@app.post("/tasks/", status_code=201)
def create_task(task: Task):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        # Check if task with same ID already exists
        cursor.execute("SELECT * FROM tasks WHERE id = %s", (task.id,))
        if cursor.fetchone():
            raise HTTPException(status_code=400, detail="Task already exists")

        # Insert the new task
        cursor.execute(
            "INSERT INTO tasks (id, title, description, completed) VALUES (%s, %s, %s, %s)",
            (task.id, task.title, task.description, task.completed)
        )
        conn.commit()

        return {"message": "Task created", "task": task}

    except Error as e:
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
@app.get("/tasks")
def get_tasks():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM tasks")
    tasks = cursor.fetchall()
    cursor.close()
    conn.close()
    return tasks

@app.post('/tasks/{tasl_id}')
def get_task_by_id(task_id:int):
    conn = get_connection()
    cursor= conn.cursor()
    cursor.execute("SELECT * FROM tasks WHERE id = %s", (task_id,))
    tasks = cursor.fetchone()
    cursor.close()
    conn.close()
    if tasks:
        return tasks
    else: 
        return f"Task with id= {task_id} not found"
    