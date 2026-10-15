# Students Database CRUD Application

A student records manager built with **FastAPI**, **SQLite** and a vanilla **HTML/CSS/JavaScript** frontend.

## Features
- Create, list, search, view, update (PATCH) and delete students
- SQLite persistence (`students.db` is created automatically)
- Validation: required fields, email/date formats, name length
- Error handling: duplicate email (409), missing student (404), empty update (400)
- Interactive API docs at `/docs`

## Project structure (flat: all files in one folder)
```
main.py          # FastAPI routes + serves the frontend
database.py      # SQLite connection + table creation
schemas.py       # Pydantic request/response models
index.html       # page layout
styles.css       # styling
app.js           # fetch() calls to the API
requirements.txt
```

## Run locally (Windows)
```
py -m venv .venv
.venv\Scripts\activate.bat
python -m pip install -r requirements.txt
python -m uvicorn main:app --reload
```
Open http://127.0.0.1:8000 (app) and http://127.0.0.1:8000/docs (Swagger UI).

On macOS/Linux, activate with `source .venv/bin/activate`.

## API
| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | /students | Create a student |
| GET | /students?search=... | List / search students |
| GET | /students/{id} | Get one student |
| PATCH | /students/{id} | Update supplied fields |
| DELETE | /students/{id} | Delete a student |

## Example body
```json
{
  "name": "Aarav Sharma",
  "date_of_birth": "2005-06-14",
  "email": "aarav@example.com",
  "phone": "9876543210",
  "course": "B.Tech Computer Science",
  "address": "Bhopal",
  "enrollment_date": "2025-08-01"
}
```


