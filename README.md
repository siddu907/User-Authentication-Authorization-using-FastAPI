# User Authentication & Authorization using FastAPI

This project implements a secure task manager API with:

- user registration and login
- password hashing with bcrypt
- JWT-based authentication
- protected task endpoints
- user-specific task ownership enforcement
- logout support via token blacklist

## Project Structure

- main.py: FastAPI app entry point
- routers/auth.py: signup, login, logout, current user routes
- routers/task.py: task CRUD routes
- crud.py: reusable database operations
- models.py: SQLAlchemy database models
- schemas.py: request/response validation models
- oauth2.py: JWT authentication helpers
- token_blacklist.py: logout support

## Setup

1. Create and activate a Python environment.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Start the API:
   ```bash
   python run.py
   ```
   or
   ```bash
   uvicorn main:app --reload
   ```

## API Endpoints

### Authentication
- POST /auth/signup
- POST /auth/login
- POST /auth/logout
- GET /auth/me
- POST /auth/refresh
- POST /auth/verify-email
- POST /auth/forgot-password
- POST /auth/reset-password
- GET /auth/admin

### Optional features included
- Refresh-token based session renewal
- Logout with token blacklisting
- Email verification flow
- Password reset flow
- Admin-role access control
- Lightweight request-rate limiting

### Tasks
- POST /tasks
- GET /tasks
- GET /tasks/{id}
- PUT /tasks/{id}
- DELETE /tasks/{id}

## Testing

Run the automated tests:

```bash
pytest -q
```
