# AI Usage and Decision Log

## 1. Purpose

This document describes how AI assistance was used during the design, implementation, testing, and deployment of the Clinic Booking API.

AI was used as a development assistant to explore implementation options, explain unfamiliar concepts, identify potential edge cases, troubleshoot errors, and support technical decision-making. The final implementation decisions were reviewed against the project's requirements and verified through code execution, API testing, or deployment checks where applicable.

AI-generated suggestions were treated as recommendations rather than automatically accepted solutions.

## 2. Architecture and Technology Decisions

### FastAPI for the REST API

**Decision:** Use FastAPI to expose the clinic booking functionality through REST endpoints.

**AI assistance:** AI helped explain API structure, route organization, request validation, HTTP methods, and appropriate response codes.

**Reasoning:** FastAPI provides typed request handling, automatic API documentation, and a straightforward way to organize endpoints into routers.

**Verification:** The application was started and its interactive Swagger documentation was accessed through `/docs`.

### SQLAlchemy and PostgreSQL

**Decision:** Use SQLAlchemy as the ORM and PostgreSQL as the persistent database.

**AI assistance:** AI helped explain the separation between database models, request schemas, database sessions, and configuration.

**Reasoning:** SQLAlchemy provides a structured interface for database operations, while PostgreSQL supports relational constraints and persistent appointment records.

**Verification:** Database connectivity was checked against Neon PostgreSQL, and database migrations were applied.

### Neon for hosted database storage

**Decision:** Use Neon PostgreSQL for the deployed application rather than depending on a local database server.

**AI assistance:** AI helped with environment-variable configuration and diagnosing database connectivity issues.

**Reasoning:** A hosted database allows the deployed API to access persistent data independently of the developer's machine.

**Verification:** The application was configured with `DATABASE_URL`, and a database connection check was performed.

## 3. Appointment Scheduling Decisions

### Fixed 30-minute slots

**Decision:** Represent appointments as 30-minute slots.

**AI assistance:** AI helped reason through how availability should be generated from a doctor's working hours.

**Reasoning:** A fixed duration simplifies slot generation, conflict detection, and availability responses for the assessment requirements.

**Verification:** Availability and booking behavior were tested against the configured working hours.

### Working hours and timezones

**Decision:** Validate appointments against the doctor's schedule and handle appointment times using timezone-aware datetimes.

**AI assistance:** AI helped identify scheduling edge cases, including appointments outside working hours, past appointments, and differences between local and UTC time.

**Reasoning:** Consistent timezone handling is essential to avoid accepting appointments at the wrong local time.

**Verification:** Appointment requests were tested against scheduling rules, including future-time validation.

### Preventing double booking

**Decision:** Reject appointment requests that conflict with an existing active appointment for the same doctor.

**AI assistance:** AI helped evaluate the validation steps required before accepting a booking.

**Reasoning:** A slot that is already occupied must not be offered or booked again.

**Verification:** Booking validation and availability behavior were tested. Additional concurrent-booking tests and database-level protection should be considered for production hardening.

### Minimum one-hour advance booking

**Decision:** Enforce a minimum one-hour interval between the booking request and appointment start time.

**AI assistance:** AI helped clarify how the time difference should be validated and how to interpret rejection messages.

**Reasoning:** This rule prevents last-minute bookings and was included as a scheduling constraint.

**Verification:** An appointment that did not satisfy the advance-booking rule was rejected, while a qualifying future appointment was accepted.

## 4. Cancellation and Rescheduling

### Cancellation with a reason

**Decision:** Require a cancellation reason and prevent an already-cancelled appointment from being cancelled again.

**AI assistance:** AI helped identify the necessary validation and state-transition checks.

**Reasoning:** Recording a reason provides context for cancellations, while preventing repeated cancellation keeps appointment state consistent.

**Verification:** Cancellation behavior was checked through the API.

### Rescheduling

**Decision:** Validate the requested replacement slot before rescheduling an appointment.

**AI assistance:** AI helped outline checks for unavailable slots, invalid appointment states, and cancelled appointments.

**Reasoning:** Rescheduling must not create conflicts or allow a cancelled appointment to become active unintentionally.

**Verification:** The rescheduling endpoint was exercised through the API. The old slot should also be verified as available after a successful reschedule.

## 5. Testing and Database Safety

**Decision:** Use pytest for automated testing and keep the standalone database connectivity check separate from test discovery.

**AI assistance:** AI helped diagnose a CI failure caused by `test_db_connection.py` connecting to `localhost:5432` during pytest collection.

**Reasoning:** A connectivity script is an operational check, not necessarily an automated test. Running it during CI collection caused the workflow to fail when no local PostgreSQL server was available.

**Change made:** The script was renamed to `check_db_connection.py`, allowing it to be run manually without automatic pytest discovery.

**Verification:** The automated test suite was run locally and through GitHub Actions.

**Safety consideration:** Automated tests should not unintentionally create, cancel, or reschedule records in the live Neon database. Tests that require persistence should use controlled fixtures or a dedicated test database.

## 6. Deployment and CI/CD

**Decision:** Use FastAPI Cloud for hosting and GitHub Actions for automated testing and deployment.

**AI assistance:** AI helped troubleshoot deployment configuration, Python packaging, environment variables, workflow YAML, and CI failures.

**Reasoning:** Automated workflows reduce repetitive manual steps and help detect problems when changes are pushed or pull requests are opened.

**Implementation:** The testing workflow runs on pushes to `master` and pull requests targeting `master`. The deployment workflow is configured to deploy on pushes to `master`.

**Verification:** Workflow logs were reviewed to diagnose dependency installation and authentication issues. Final successful runs should be confirmed before considering deployment fully verified.

## 7. How AI Recommendations Were Evaluated

AI assistance was used to:

- Explain technical concepts and unfamiliar errors.
- Compare implementation approaches.
- Identify validation rules and edge cases.
- Suggest changes to project configuration and CI workflows.
- Help organize documentation and deployment steps.

Recommendations were evaluated against the assessment requirements, the existing codebase, and observed runtime behavior. When an error occurred, its logs were used to guide the next troubleshooting step instead of assuming the proposed solution had worked.

## 8. Limitations and Remaining Considerations

AI assistance does not guarantee correctness, security, or production readiness. The following areas require continued engineering attention:

- Protecting appointment creation against concurrent booking requests.
- Enforcing data integrity at the database level where appropriate.
- Testing daylight-saving and timezone boundary behavior where relevant.
- Validating authorization and patient-data access before real clinical use.
- Ensuring automated tests do not affect production records.
- Monitoring deployment health and handling database connection failures.

