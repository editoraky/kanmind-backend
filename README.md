# KanMind — Backend API

A Kanban-style project management backend in the spirit of Trello. KanMind lets
users create boards, invite members, organise work into tasks across four
workflow stages, and discuss those tasks through comments — all behind a
token-authenticated REST API.

Built with Django and the Django REST Framework as a learning project, with a
strong focus on clean separation of concerns: every app keeps its data models,
serializers, views, URLs and permissions in their own dedicated places.

---

## Tech Stack

| Layer            | Technology                          |
|------------------|-------------------------------------|
| Language         | Python 3.14                         |
| Web framework    | Django 6.0                          |
| API framework    | Django REST Framework 3.17          |
| Authentication   | DRF Token Authentication            |
| Database         | SQLite (development)                |
| Config           | python-dotenv (`.env` file)         |
| CORS             | django-cors-headers                 |

---

## Project Structure

The project follows the course conventions: the configuration package is named
`core`, and every app carries a speaking suffix. Each app exposes its API
through a dedicated `api/` sub-package.

```
backend/
├── core/                 # Project config: settings, root URL routing, wsgi
│   ├── settings.py
│   └── urls.py
├── auth_app/             # Registration, login, email-check
│   └── api/              # serializers, views, urls
├── kanban_app/           # Boards, tasks, comments
│   └── api/              # serializers, views, urls, permissions
├── manage.py
├── requirements.txt
├── .env.example          # Template for the required .env file
└── README.md
```

---

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/editoraky/kanmind-backend.git
cd kanmind-backend
```

### 2. Create and activate a virtual environment

**Windows (PowerShell):**

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

**macOS / Linux:**

```bash
python -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Create the environment file

The secret key is **not** stored in the repository. Copy the provided template
and fill in your own value:

**Windows (PowerShell):**

```powershell
Copy-Item .env.example .env
```

**macOS / Linux:**

```bash
cp .env.example .env
```

Then open `.env` and set the `DJANGO_SECRET_KEY` variable. Any long, random
string works for local development:

```
DJANGO_SECRET_KEY=your-generated-secret-key-here
```

### 5. Apply database migrations

This creates a fresh local `db.sqlite3` from the migration files.

```bash
python manage.py migrate
```

### 6. Create an admin user (optional, for the admin interface)

```bash
python manage.py createsuperuser
```

### 7. Start the development server

```bash
python manage.py runserver
```

The API is now available at `http://127.0.0.1:8000/`.

---

## API Endpoints

All endpoints live under the `/api/` prefix. Every endpoint except registration
and login requires a valid token, sent as an `Authorization: Token <token>`
header.

### Authentication

| Method | Path                  | Purpose                                  |
|--------|-----------------------|------------------------------------------|
| POST   | `/api/registration/`  | Create a new user, returns a token       |
| POST   | `/api/login/`         | Authenticate, returns a token            |
| GET    | `/api/email-check/`   | Check whether an email is already in use |

### Boards

| Method | Path                  | Purpose                                  |
|--------|-----------------------|------------------------------------------|
| GET    | `/api/boards/`        | List boards the user owns or belongs to  |
| POST   | `/api/boards/`        | Create a new board                       |
| GET    | `/api/boards/{id}/`   | Retrieve one board including its tasks   |
| PATCH  | `/api/boards/{id}/`   | Update a board's title and members       |
| DELETE | `/api/boards/{id}/`   | Delete a board (owner only)              |

### Tasks

| Method | Path                          | Purpose                              |
|--------|-------------------------------|--------------------------------------|
| GET    | `/api/tasks/assigned-to-me/`  | Tasks where the user is the assignee |
| GET    | `/api/tasks/reviewing/`       | Tasks where the user is the reviewer |
| POST   | `/api/tasks/`                 | Create a task on a board             |
| PATCH  | `/api/tasks/{id}/`            | Update a task                        |
| DELETE | `/api/tasks/{id}/`            | Delete a task (creator or board owner)|

### Comments

| Method | Path                                       | Purpose                  |
|--------|--------------------------------------------|--------------------------|
| GET    | `/api/tasks/{id}/comments/`                | List a task's comments   |
| POST   | `/api/tasks/{id}/comments/`                | Add a comment to a task  |
| DELETE | `/api/tasks/{id}/comments/{comment_id}/`   | Delete a comment (author)|

For full request and response details, see the API documentation that
accompanies the project.

---

## Notable Details

- **Token authentication.** Obtain a token via `/api/registration/` or
  `/api/login/`, then send it on every other request as the header
  `Authorization: Token <your-token>`.
- **Status values** for tasks are fixed: `to-do`, `in-progress`, `review`,
  `done`. **Priority values** are `low`, `medium`, `high`.
- **Layered permissions.** Access is enforced per resource and per HTTP method.
  For example, any board member may read a board, but only the owner may delete
  it; only a task's creator or the board owner may delete that task; only a
  comment's author may delete it.
- **Cascade deletes.** Deleting a board removes its tasks and their comments;
  deleting a task removes its comments.
- **CORS** is enabled for all origins to allow a separately hosted frontend to
  call the API during development.
- **The database is never committed.** `db.sqlite3` is git-ignored; each
  environment builds its own database from the migration files.
- **The secret key is never committed.** It is read from the environment
  variable `DJANGO_SECRET_KEY`; the app fails fast on startup if it is missing,
  so make sure your `.env` file is in place before running the server.

---

## License

This project was created for educational purposes as part of a backend
development course.