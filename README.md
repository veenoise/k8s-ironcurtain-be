#  Iron Curtain — Backend

A story-driven, Cold War-themed Capture The Flag (CTF) backend built with FastAPI.

## Tech Stack

- **Framework:** FastAPI (Python 3.13)
- **ORM:** Prisma Client Python (PostgreSQL)
- **Auth:** JWT (HS256) + bcrypt
- **File Storage:** Local filesystem (`uploads/`)

## Setup

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

Configure `.env` (see `.env.example`):

```env
DATABASE_URL="postgresql://user:pass@localhost:5432/ironcurtain"
JWT_SECRET="change-me-to-a-strong-random-secret-in-production"
ADMIN_USERNAME="admin"
ADMIN_PASSWORD="changeme"
```

Run database migrations and generate the Prisma client:

```bash
prisma migrate dev
PATH=".venv/bin:$PATH" prisma generate
```

## Running

```bash
uvicorn app.main:app --reload
```

## Seed

Create an admin account (reads `ADMIN_USERNAME`/`ADMIN_PASSWORD` from `.env`):

```bash
python seed/admin.py
```

Reset all user scores and submissions:

```bash
python seed/reset.py
```

## API Endpoints

### Auth (`/api/v1/auth`)

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/register` | No | Register a new user |
| POST | `/login` | No | Login, returns JWT |
| POST | `/logout` | Bearer | Logout (client discards token) |

### Challenges (`/api/v1/challenges`)

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `—` | Bearer | List challenges with questions and files |
| POST | `/submit` | Bearer | Submit a flag for a question |
| GET | `/{qid}/files/{fid}/download` | Bearer | Download question file |

### Scoreboard (`/api/v1/scoreboard`)

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `—` | No | Top 100 users by score |

### Admin (`/api/v1/admin`) — requires `role: admin`

| Method | Path | Description |
|--------|------|-------------|
| POST | `/challenges` | Create a challenge |
| PUT | `/challenges/{id}` | Update a challenge |
| DELETE | `/challenges/{id}` | Delete a challenge |
| POST | `/questions` | Create question (multipart, accepts multiple files) |
| PUT | `/questions/{id}` | Update question, append files |
| DELETE | `/questions/{id}` | Delete a question |
| DELETE | `/questions/{id}/files/{fid}` | Delete a specific file |

## Database Schema

- **User** — `id`, `username`, `passwordHash`, `role` (user/admin), `score`, `createdAt`
- **Challenge** — `id`, `name`, `codename`, `description`, `storyOrder`
- **Question** — `id`, `title`, `prompt`, `points`, `flagHash` (SHA-256), `challengeId`
- **File** — `id`, `questionId`, `fileName`, `filePath`, `createdAt`
- **Submission** — `id`, `userId`, `questionId`, `isCorrect`, `submittedAt`

Flags are stored as SHA-256 hashes. Plaintext flags are never stored in the database.

## Docker build

```bash
docker build -t k8s-ironcurtain-be:latest .
```

## Docker compose

```bash
docker compose up -d
```