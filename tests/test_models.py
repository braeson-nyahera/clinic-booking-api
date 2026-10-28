
from app.models import Appointment, Doctor, Patient, WorkingHours


def test_models_are_registered():
    assert Doctor.__tablename__ == "doctors"
    assert Patient.__tablename__ == "patients"
    assert WorkingHours.__tablename__ == "working_hours"
    assert Appointment.__tablename__ == "appointments"
