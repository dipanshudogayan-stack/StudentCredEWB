import sqlite3
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException, Query, Response, status
from fastapi.responses import FileResponse

from database import db, init_db
from schemas import StudentCreate, StudentResponse, StudentUpdate

BASE_DIR = Path(__file__).resolve().parent

COLUMNS = ["name", "date_of_birth", "email", "phone", "course", "address", "enrollment_date"]
REQUIRED = {"name", "date_of_birth", "email"}


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="Students CRUD API",
    description="Create, read, update and delete student records (FastAPI + SQLite).",
    version="1.0.0",
    lifespan=lifespan,
)


def fetch_student(connection: sqlite3.Connection, student_id: int) -> sqlite3.Row:
    row = connection.execute("SELECT * FROM students WHERE id = ?", (student_id,)).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="Student not found.")
    return row


@app.get("/", include_in_schema=False)
def home():
    return FileResponse(BASE_DIR / "index.html")


@app.get("/styles.css", include_in_schema=False)
def styles():
    return FileResponse(BASE_DIR / "styles.css", media_type="text/css")


@app.get("/app.js", include_in_schema=False)
def script():
    return FileResponse(BASE_DIR / "app.js", media_type="application/javascript")


@app.post("/students", response_model=StudentResponse, status_code=status.HTTP_201_CREATED)
def create_student(student: StudentCreate):
    data = student.model_dump(mode="json")
    placeholders = ", ".join("?" for _ in COLUMNS)
    try:
        with db() as connection:
            cursor = connection.execute(
                f"INSERT INTO students ({', '.join(COLUMNS)}) VALUES ({placeholders})",
                [data[c] for c in COLUMNS],
            )
            return dict(fetch_student(connection, cursor.lastrowid))
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=409, detail="A student with this email already exists.")


@app.get("/students", response_model=list[StudentResponse])
def list_students(search: str | None = Query(default=None)):
    sql = "SELECT * FROM students"
    params: list[str] = []
    if search and search.strip():
        like = f"%{search.strip()}%"
        sql += " WHERE name LIKE ? OR email LIKE ? OR course LIKE ?"
        params = [like, like, like]
    sql += " ORDER BY id DESC"
    with db() as connection:
        return [dict(r) for r in connection.execute(sql, params).fetchall()]


@app.get("/students/{student_id}", response_model=StudentResponse)
def get_student(student_id: int):
    with db() as connection:
        return dict(fetch_student(connection, student_id))


@app.patch("/students/{student_id}", response_model=StudentResponse)
def update_student(student_id: int, changes: StudentUpdate):
    updates = changes.model_dump(exclude_unset=True, mode="json")
    if not updates:
        raise HTTPException(status_code=400, detail="No fields provided to update.")
    for field in REQUIRED & updates.keys():
        if updates[field] is None:
            raise HTTPException(status_code=400, detail=f"'{field}' cannot be empty.")
    # Column names come from the schema's fixed fields; values are parameterized.
    columns = ", ".join(f"{column} = ?" for column in updates)
    values = list(updates.values()) + [student_id]
    try:
        with db() as connection:
            fetch_student(connection, student_id)  # 404 if missing
            connection.execute(f"UPDATE students SET {columns} WHERE id = ?", values)
            return dict(fetch_student(connection, student_id))
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=409, detail="A student with this email already exists.")


@app.delete("/students/{student_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_student(student_id: int):
    with db() as connection:
        cursor = connection.execute("DELETE FROM students WHERE id = ?", (student_id,))
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Student not found.")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
