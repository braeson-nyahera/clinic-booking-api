# Clinic Booking API

A REST API for managing clinic appointments, built with Python, FastAPI, SQLAlchemy, and PostgreSQL. The system supports doctor availability, appointment booking, cancellation, rescheduling, and patient appointment history.

## Project Overview

The API is designed for a clinic with five doctors and 30-minute appointment slots. It validates appointment requests against doctors' working hours, prevents conflicting bookings, and enforces a minimum one-hour advance-booking window.

### Features

- Retrieve available 30-minute slots for a doctor on a specific date.
- Book appointments within configured working hours.
- Prevent double booking.
- Reject appointments in the past or with insufficient advance notice.
- Cancel appointments with a recorded reason.
- Reschedule appointments after validating the requested slot.
- Retrieve a patient's upcoming appointments in chronological order.
- Validate request data and return meaningful HTTP errors.
- Store application data in Neon PostgreSQL.
- Manage database schema changes with Alembic.
- Provide interactive API documentation through Swagger UI.

## Technology Stack

| Technology | Purpose |
|---|---|
| Python 3.12 | Programming language |
| FastAPI | REST API framework |
| SQLAlchemy | Database ORM |
| PostgreSQL (Neon) | Persistent data storage |
| Pydantic | Request validation and settings |
| Alembic | Database migrations |
| Pytest | Automated testing |
| Uvicorn | ASGI application server |
| GitHub Actions | CI/CD automation |
| FastAPI Cloud | Application hosting |

## Project Structure

```text
clinic-booking-api/
├── .github/
│   └── workflows/
│       ├── deploy.yml
│       └── tests.yml
├── app/
│   ├── main.py
│   ├── config.py
│   ├── database.py
│   ├── models/
│   ├── routers/
│   └── schemas/
├── migrations/
├── scripts/
│   └── seed_data.py
├── tests/
├── .env.example
├── alembic.ini
├── pyproject.toml
├── requirements.txt
├── check_db_connection.py
└── README.md
```

## Data Model

The application uses four primary entities.

- **Doctor:** Stores doctor details, specialty, and active status.
- **Patient:** Stores patient details and a unique email address.
- **WorkingHours:** Defines a doctor's weekly schedule.
- **Appointment:** Stores the doctor, patient, appointment time, status, and cancellation reason.

Appointments have a fixed duration of 30 minutes. Clinic scheduling uses the `Africa/Nairobi` timezone.

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | Root endpoint |
| GET | `/health` | Application health check |
| GET | `/health/db` | Database connectivity check |
| GET | `/doctors/{doctor_id}/availability?date=YYYY-MM-DD` | Retrieve available slots |
| POST | `/appointments` | Book an appointment |
| PATCH | `/appointments/{appointment_id}/cancel` | Cancel an appointment |
| PATCH | `/appointments/{appointment_id}/reschedule` | Reschedule an appointment |
| GET | `/patients/{patient_id}/appointments` | Retrieve upcoming patient appointments |

### Book an Appointment

`POST /appointments`

Request body:

```json
{
  "doctor_id": 1,
  "patient_id": 1,
  "start_at": "2026-11-02T10:00:00+03:00"
}
```

The requested time must include a timezone, be sufficiently far in the future, fall within the doctor's working hours, and not conflict with another active booking.

### Cancel an Appointment

`PATCH /appointments/{appointment_id}/cancel`

Request body:

```json
{
  "reason": "Patient requested cancellation"
}
```

The cancellation reason is recorded, and the cancelled appointment no longer blocks availability. An appointment that has already been cancelled cannot be cancelled again.

### Reschedule an Appointment

`PATCH /appointments/{appointment_id}/reschedule`

Request body:

```json
{
  "new_start_at": "2026-11-02T11:00:00+03:00"
}
```

The new slot must satisfy the scheduling rules and must not conflict with another active booking. Cancelled appointments cannot be rescheduled.

### HTTP Status Codes

| Status | Meaning |
|---|---|
| `200 OK` | Request completed successfully |
| `201 Created` | Appointment created successfully |
| `400 Bad Request` | Scheduling rule violated |
| `404 Not Found` | Requested resource not found |
| `409 Conflict` | Slot unavailable or appointment already cancelled |
| `422 Unprocessable Entity` | Request validation failed |
| `500 Internal Server Error` | Unexpected server-side error |

## Local Setup

### Prerequisites

- Python 3.12
- Git
- A PostgreSQL database, such as Neon

### 1. Clone the repository

```bash
git clone https://github.com/braeson-nyahera/clinic-booking-api.git
cd clinic-booking-api
```

### 2. Create a virtual environment

```bash
python3.12 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the project root:

```env
DATABASE_URL=your_postgresql_connection_string
```

Use the connection string format supported by the application's SQLAlchemy driver and configure SSL as required by your database provider.

**Security:** Never commit `.env` or expose database credentials. Use environment variables or platform secrets in production.

### 5. Apply database migrations

```bash
alembic upgrade head
```

This applies the database schema changes defined in the migration history.

### 6. Add sample data

If the database has not been seeded, run:

```bash
python -m scripts.seed_data
```

The seed script creates sample doctor, patient, and working-hours records if they do not already exist.

### 7. Start the application

```bash
uvicorn app.main:app --reload
```

The local API will be available at `http://127.0.0.1:8000`.

Interactive documentation: `http://127.0.0.1:8000/docs`

Alternative documentation: `http://127.0.0.1:8000/redoc`

## Testing

Run automated tests from the project root:

```bash
python -m pytest -v
```

Compile the application modules with:

```bash
python -m compileall app
```

The standalone database connectivity check can be run separately:

```bash
python check_db_connection.py
```

**Database safety:** Tests or scripts that connect to Neon may create or modify persistent data. Review their behavior before running them against a production database.

## Deployment

The application is hosted on FastAPI Cloud, with Neon PostgreSQL providing persistent storage.

- **Public API URL:** https://clinic-booking-api.fastapicloud.dev/
- **Swagger UI:** https://clinic-booking-api.fastapicloud.dev/docs

Configure `DATABASE_URL` in the hosting platform's environment variables or secrets. Ensure the database migrations have been applied and the deployed application starts successfully.

## CI/CD

The repository contains two GitHub Actions workflows.

### Continuous Integration

The `tests.yml` workflow is configured to run on pushes to `master` and pull requests targeting `master`. It installs dependencies, compiles the application, and runs the automated test suite.

### Continuous Deployment

The `deploy.yml` workflow is configured to deploy to FastAPI Cloud on pushes to `master`. It uses the `FASTAPI_CLOUD_TOKEN` and `FASTAPI_CLOUD_APP_ID` GitHub repository secrets.

The deployment workflow requires valid credentials. Confirm that the latest workflow run succeeds before describing automatic deployment as fully verified.

Workflow runs: https://github.com/braeson-nyahera/clinic-booking-api/actions

## AI Assistance Reflection

AI assistance was used during development to help structure the FastAPI application, explain SQLAlchemy models and Alembic migrations, and implement endpoint validation and error handling.

The suggestions were reviewed and tested during implementation rather than accepted automatically. Particular care was required around timezone-aware scheduling, appointment conflicts, cancellation and rescheduling rules, database connectivity, and automated testing.

AI assistance helped accelerate development and clarify unfamiliar concepts. The developer remains responsible for verifying the implementation, protecting credentials, testing edge cases, and confirming the behavior of the deployed application.

- [AI Usage and Decision Log](AI_USAGE.md)

## Project Links

- **GitHub repository:** https://github.com/braeson-nyahera/clinic-booking-api
- **Public API:** https://clinic-booking-api.fastapicloud.dev
- **API documentation:** https://clinic-booking-api.fastapicloud.dev/docs
