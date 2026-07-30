from datetime import datetime


class ServiceError(Exception):
    """Base class for all service layer errors in this application."""


class NotFoundError(ServiceError):
    """Base class for errors where a requested resource does not exist."""


class DoctorNotFound(NotFoundError):
    def __init__(self, doctor_id: int):
        self.doctor_id = doctor_id
        super().__init__(f"Doctor with id {doctor_id} does not exist.")


class PatientNotFound(NotFoundError):
    def __init__(self, patient_id: int):
        self.patient_id = patient_id
        super().__init__(f"Patient with id {patient_id} does not exist.")


class AppointmentNotFound(NotFoundError):
    def __init__(self, appointment_id: int):
        self.appointment_id = appointment_id
        super().__init__(f"Appointment with id {appointment_id} does not exist.")


class BusinessRuleViolation(ServiceError):
    """Base class for errors where the request is well formed but violates
    a booking rule.
    """


class OutsideWorkingHoursError(BusinessRuleViolation):
    def __init__(self, doctor_id: int, start_time: datetime):
        self.doctor_id = doctor_id
        self.start_time = start_time
        super().__init__(f"Doctor {doctor_id} does not work at {start_time.isoformat()}.")


class OffSlotGridError(BusinessRuleViolation):
    def __init__(self, start_time: datetime):
        self.start_time = start_time
        super().__init__(
            f"Start time {start_time.isoformat()} does not fall on a 30 minute slot boundary."
        )


class InsufficientLeadTimeError(BusinessRuleViolation):
    def __init__(self, start_time: datetime, now: datetime):
        self.start_time = start_time
        self.now = now
        super().__init__(
            f"Start time {start_time.isoformat()} does not provide at least "
            f"1 hour of notice from the current time {now.isoformat()}."
        )


class ConflictError(ServiceError):
    """Base class for errors where the request conflicts with existing state."""


class SlotAlreadyBookedError(ConflictError):
    def __init__(self, doctor_id: int, start_time: datetime):
        self.doctor_id = doctor_id
        self.start_time = start_time
        super().__init__(
            f"Doctor {doctor_id} already has a booked appointment at {start_time.isoformat()}."
        )


class AppointmentAlreadyCancelledError(ConflictError):
    def __init__(self, appointment_id: int):
        self.appointment_id = appointment_id
        super().__init__(f"Appointment {appointment_id} is already cancelled.")
