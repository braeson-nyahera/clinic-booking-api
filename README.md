
# Clinic Booking API

## 1. Project Overview

The Clinic Booking API is a REST API for a small clinic with five doctors. Patients can view available appointment slots, book appointments, cancel existing bookings, and reschedule appointments.

The system uses Python, FastAPI, SQLAlchemy, and Neon PostgreSQL. It is designed to support the clinic's current needs while allowing future growth.

## 2. System Architecture

The system consists of the following components:

- **API layer:** FastAPI exposes REST endpoints and handles HTTP requests and responses.
- **Validation layer:** Pydantic validates request data, while application-level rules enforce booking requirements.
- **Business logic layer:** Services manage availability, booking, cancellation, and rescheduling.
- **Data access layer:** SQLAlchemy manages database queries and transactions.
- **Database:** Neon PostgreSQL stores doctors, patients, working hours, and appointments.
- **Testing:** Pytest verifies business rules and API behavior.
- **Deployment and CI/CD:** GitHub Actions runs automated tests on pull requests and deploys changes after merges into the designated branch.

## 3. Database Design

### 3.1 Doctor

Stores information about each doctor.

Fields:

- `id`: Primary key.
- `name`: Doctor's name.
- `specialty`: Medical specialty.
- `is_active`: Indicates whether the doctor can receive bookings.

Relationships:

- One doctor can have multiple working-hour records.
- One doctor can have multiple appointments.

### 3.2 Patient

Stores patient information.

Fields:

- `id`: Primary key.
- `name`: Patient's name.
- `email`: Patient's email address, with a uniqueness constraint.

Relationships:

- One patient can have multiple appointments.

### 3.3 WorkingHours

Defines a doctor's recurring weekly working schedule.

Fields:

- `id`: Primary key.
- `doctor_id`: Foreign key referencing `Doctor`.
- `day_of_week`: Day of the week.
- `start_time`: Start of the working period.
- `end_time`: End of the working period.

A doctor can have different working hours on different days. The design can be extended to support exceptions, leave, and public holidays.

### 3.4 Appointment

Stores appointment bookings and their current status.

Fields:

- `id`: Primary key.
- `doctor_id`: Foreign key referencing `Doctor`.
- `patient_id`: Foreign key referencing `Patient`.
- `start_at`: Appointment start timestamp.
- `end_at`: Appointment end timestamp.
- `status`: Booking status, such as `booked` or `cancelled`.
- `cancellation_reason`: Reason provided when cancelling.
- `created_at`: Timestamp when the appointment was created.
- `updated_at`: Timestamp of the most recent update.

Appointments have a fixed duration of 30 minutes. The API enforces valid slot boundaries and uses a consistent timezone strategy for timestamps.

## 4. System Workflows

### 4.1 Checking Availability

1. A patient requests availability for a doctor and date.
2. The API retrieves the doctor's working hours and existing appointments.
3. The API generates 30-minute slots within the working period.
4. Past slots and slots occupied by active appointments are excluded.
5. The API returns the remaining available slots.

### 4.2 Booking an Appointment

1. The patient submits a booking request.
2. The API validates the doctor, patient, requested date, working hours, and slot boundaries.
3. The system checks for conflicting appointments.
4. A database transaction creates the appointment if the slot remains available.
5. The API returns the appointment details or a meaningful error response.

### 4.3 Cancelling an Appointment

1. The patient or authorized caller submits a cancellation reason.
2. The API checks whether the appointment exists and is active.
3. The appointment status changes to `cancelled`.
4. The cancelled appointment no longer blocks the slot.
5. Repeated cancellation requests return an appropriate error.

### 4.4 Rescheduling an Appointment

1. The caller submits a new appointment time.
2. The API checks that the appointment exists and is not cancelled.
3. The requested replacement slot is validated against working hours, past-time restrictions, and existing bookings.
4. The appointment is updated within a database transaction.
5. If rescheduling fails, the original appointment remains unchanged.

## 5. Preventing Double Bookings

Checking availability before inserting an appointment is insufficient because multiple requests may arrive simultaneously.

The design therefore uses PostgreSQL database-level protection to prevent two active appointments for the same doctor from having the same start time. The API also validates slot boundaries and uses transactions when creating or changing bookings.

This approach assumes appointments have a fixed duration of 30 minutes and start on valid slot boundaries. If appointment durations become variable, an interval-overlap constraint will be required instead.

A booking conflict returns HTTP `409 Conflict`.

## 6. API Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| `POST` | `/appointments` | Book an appointment. |
| `GET` | `/doctors/{id}/availability?date=YYYY-MM-DD` | Retrieve available 30-minute slots. |
| `PATCH` | `/appointments/{id}/cancel` | Cancel an appointment with a reason. |
| `PATCH` | `/appointments/{id}/reschedule` | Move an appointment to another slot. |
| `GET` | `/patients/{id}/appointments` | Retrieve upcoming appointments (bonus). |

The API will return meaningful validation errors and appropriate HTTP status codes, including:

- `400 Bad Request`: Invalid operation or business-rule violation.
- `404 Not Found`: Doctor, patient, or appointment does not exist.
- `409 Conflict`: Appointment slot is already booked or the requested state transition is invalid.
- `422 Unprocessable Entity`: Request data fails validation.
- `500 Internal Server Error`: Unexpected server-side failure.

## 7. Design Decisions and Trade-offs

### FastAPI

FastAPI provides typed request validation, asynchronous request handling where appropriate, and automatic OpenAPI documentation.

### Neon PostgreSQL

Neon provides managed PostgreSQL storage without requiring a locally hosted database. The connection string is supplied through environment variables.

### SQLAlchemy

SQLAlchemy separates database operations from HTTP endpoint logic and provides transaction management.

### Fixed 30-minute appointments

Fixed-duration slots simplify availability calculations and conflict detection. Variable-duration appointments would require more complex interval-overlap validation.

### Database constraints

Database-level protection prevents conflicting bookings even when concurrent requests occur.

### Cancellation instead of deletion

Cancelled appointments remain in the database to preserve booking history. Their slots can be booked again.

### Recurring working hours

Recurring schedules reduce duplication. Future support for holidays, leave, and exceptional working days will require additional scheduling rules.

### Layered code structure

Separating routing, schemas, business logic, and database access improves maintainability and testability.

## 8. Assumptions and Future Improvements

The initial implementation assumes:

- The clinic has five doctors at launch.
- Doctors have recurring weekly working hours.
- All appointments last 30 minutes.
- Patients have existing records before booking.
- Appointment timestamps are handled consistently using an explicitly configured timezone.
- Authentication and authorization are outside the initial scope unless time permits.


## 9. Testing Strategy

Automated tests will cover:

- Successful appointment booking.
- Invalid doctor or patient identifiers.
- Booking outside working hours.
- Booking appointments in the past.
- Booking unavailable slots.
- Concurrent booking conflicts.
- Successful cancellation.
- Cancellation of an already cancelled appointment.
- Successful rescheduling.
- Failed rescheduling without losing the original appointment.
- Attempts to reschedule cancelled appointments.
- Upcoming appointments sorted by date.

Tests will use an isolated test database so they do not modify production data.

## 10. Deployment and CI/CD

The API will be deployed to a cloud hosting provider and connected to Neon PostgreSQL through environment variables.

GitHub Actions will:

1. Install project dependencies.
2. Run automated tests on pull requests.
3. Prevent failed checks from passing the required CI checks.
4. Trigger deployment after changes are merged into the designated branch.

Database credentials and deployment secrets will be stored in the relevant environment configuration and GitHub Actions secrets, not committed to the repository.

The public application URL, deployment branch, and pipeline details will be added after deployment is configured and verified.

## 11. AI Reflection

This section will be completed after implementation.

It will describe:

1. How AI was used across system design, implementation, deployment, and testing.
2. One example of an AI suggestion that improved the work, including the prompt used.
3. One incorrect or incomplete AI suggestion and how it was identified.
4. Two decisions made independently and why personal judgment was trusted.

The reflection will document actual experiences rather than hypothetical examples.

## 12. Local Development

The project uses Python and a virtual environment.

To run the application locally:

1. Clone the repository.
2. Create and activate a Python virtual environment.
3. Install dependencies from `requirements.txt`.
4. Configure `DATABASE_URL` in `.env`.
5. Apply database migrations.
6. Start the API using Uvicorn.

The final installation commands, deployment URL, and API documentation URL will be added after implementation and deployment have been verified.
