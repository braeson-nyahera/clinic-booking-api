# Clinic Booking API

A REST API built with **FastAPI, SQLAlchemy, and PostgreSQL** for managing clinic appointments. The system allows patients to book, cancel, and reschedule appointments while checking doctor availability and working hours.

## Features

- Retrieve available 30-minute appointment slots for a doctor on a specific date.
- Book appointments within a doctor's configured working hours.
- Prevent overlapping appointments for the same doctor.
- Enforce a minimum one-hour advance-booking window.
- Cancel appointments with a recorded cancellation reason.
- Reschedule appointments after validating the new time slot.
- Retrieve a patient's upcoming appointments in chronological order.
- Validate request data and return meaningful HTTP status codes.
- Persist application data in PostgreSQL hosted on Neon.
- Manage database schema changes with Alembic migrations.
- Provide interactive API documentation through Swagger UI.

## Technology Stack

- **Language:** Python
- **API framework:** FastAPI
- **ORM:** SQLAlchemy
- **Database:** PostgreSQL (Neon)
- **Validation:** Pydantic
- **Database migrations:** Alembic
- **Testing:** Pytest
- **ASGI server:** Uvicorn

## Project Structure

```text
clinic-booking-api/
├── app/
│   ├── main.py
│   ├── config.py
│   ├── database.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── doctor.py
│   │   ├── patient.py
│   │   ├── working_hours.py
│   │   └── appointment.py
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── availability.py
│   │   └── appointment.py
│   └── routers/
│       ├── __init__.py
│       ├── doctors.py
│       ├── appointments.py
│       └── patients.py
├── migrations/
├── tests/
├── scripts/
│   └── seed_data.py
├── alembic.ini
├── requirements.txt
├── .gitignore
└── README.md
```

## Data Model

The application uses four primary database entities.

### Doctor

Stores doctor information, including name, specialty, and active status.

### Patient

Stores patient information, including name and unique email address.

### WorkingHours

Defines each doctor's working schedule using the day of the week, start time, and end time.

### Appointment

Stores appointment details, including doctor, patient, start time, end time, booking status, and cancellation reason.

Appointments have a fixed duration of 30 minutes. Clinic dates and times use the `Africa/Nairobi` timezone.

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | Root endpoint |
| GET | `/health` | Application health check |
| GET | `/health/db` | Database connectivity check |
| GET | `/doctors/{doctor_id}/availability?date=YYYY-MM-DD` | Retrieve available appointment slots |
| POST | `/appointments` | Book an appointment |
| PATCH | `/appointments/{appointment_id}/cancel` | Cancel an appointment |
| PATCH | `/appointments/{appointment_id}/reschedule` | Reschedule an appointment |
| GET | `/patients/{patient_id}/appointments` | Retrieve upcoming patient appointments |

### Booking an Appointment

**Request**

`POST /appointments`

```json
{
  "doctor_id": 1,
  "patient_id": 1,
  "start_at": "2026-11-02T10:00:00+03:00"
}
```

The requested time must include a timezone, be sufficiently far in the future, fall within the doctor's working hours, and not overlap another active appointment.

### Cancelling an Appointment

**Request**

`PATCH /appointments/1/cancel`

```json
{
  "reason": "Patient requested cancellation"
}
```

Cancellation updates the appointment status and records the reason. Cancelled appointments no longer block availability.

### Rescheduling an Appointment

**Request**

`PATCH /appointments/1/reschedule`

```json
{
  "new_start_at": "2026-11-02T11:00:00+03:00"
}
```

The new slot must satisfy the appointment scheduling rules and must not conflict with another active booking.

## HTTP Status Codes

| Status code | Meaning |
|---|---|
| `200 OK` | Request completed successfully |
| `201 Created` | Appointment created successfully |
| `400 Bad Request` | Scheduling rule violated |
| `404 Not Found` | Requested doctor, patient, or appointment not found |
| `409 Conflict` | Appointment slot unavailable or appointment already cancelled |
| `422 Unprocessable Entity` | Request validation failed |
| `500 Internal Server Error` | Unexpected server-side error |

## Prerequisites

- Python 3.10 or later
- pip
- A PostgreSQL database, such as Neon
- Git

## Local Installation

### 1. Clone the repository

Replace the placeholder with the actual repository URL.

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
cd clinic-booking-api
```

### 2. Create and activate a virtual environment

On Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the project root:

```env
DATABASE_URL=your_neon_postgresql_connection_string
```

Use the PostgreSQL connection string format supported by the application's SQLAlchemy driver. Ensure Neon SSL requirements are satisfied.

**Security:** Never commit `.env` or publish database credentials. Configure secrets through environment variables in production.

### 5. Apply database migrations

```bash
alembic upgrade head
```

This creates or updates the database schema using the project's migration history.

### 6. Add sample data

If the seed script is included in the repository:

```bash
python -m scripts.seed_data
```

The script creates sample doctor, patient, and working-hours records if they do not already exist.

### 7. Start the application

```bash
uvicorn app.main:app --reload
```

The API will be available locally at:

`http://127.0.0.1:8000`

Interactive documentation:

`http://127.0.0.1:8000/docs`

Alternative API documentation:

`http://127.0.0.1:8000/redoc`

## Testing

Run the automated tests from the project root:

```bash
pytest -v
```

The test suite should cover application health, request validation, availability, booking, cancellation, rescheduling, and error responses.

Tests that write to the configured Neon database can create or modify persistent records. Use them carefully and clean up any deliberately created test data.

## Deployment

The application is intended to be deployed to a public application hosting platform, with Neon PostgreSQL providing persistent database storage.

Production configuration should include:

- A valid `DATABASE_URL` environment variable.
- Database migrations applied before or during deployment.
- A production ASGI server command.
- A public health endpoint for deployment checks.
- Database credentials stored as platform secrets rather than in source code.

**Deployment platform:** To be added after deployment.

**Public API URL:** To be added after deployment.

**Swagger documentation URL:** `YOUR_PUBLIC_API_URL/docs`

## CI/CD

The planned GitHub Actions workflow will:

1. Install Python dependencies.
2. Run automated tests on pull requests.
3. Prevent broken changes from being merged when required checks fail.
4. Deploy the application automatically after changes are merged into the main branch.

The final README should identify the actual workflow and deployment platform once configured.

## AI Assistance Reflection

AI assistance was used during development to help structure the FastAPI application, explain SQLAlchemy models and database migrations, and implement endpoint validation and error handling.

The generated code was reviewed and tested throughout implementation. AI-generated suggestions were treated as development assistance rather than automatically assumed to be correct.

Areas requiring particular care include concurrent booking requests, database transaction safety, timezone-aware date handling, validation of working-hour configurations, and automated tests for both successful and unsuccessful operations.

AI assistance helped accelerate implementation and explain unfamiliar concepts. The developer remains responsible for verifying correctness, protecting database credentials, testing edge cases, and ensuring the deployed application behaves as expected.

## Project Status

The core API endpoints have been implemented, and the existing test suite has passed locally. Public deployment, CI/CD verification, and expanded workflow testing should be marked complete only after they have been successfully verified.
