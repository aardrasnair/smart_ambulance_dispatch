"""
hospital_models.py — Hospital data models for backend use.

Copied from src/hospital.py to avoid import issues.
"""

from enum import Enum
from typing import List, Dict, Optional, Tuple

class PatientSeverity(Enum):
    CRITICAL = 1    # Life-threatening, immediate attention required
    URGENT = 2      # Serious but not immediately life-threatening
    MODERATE = 3    # Requires medical attention but can wait
    MILD = 4        # Minor injuries/conditions

class DoctorSpecialty(Enum):
    EMERGENCY = "Emergency Medicine"
    TRAUMA = "Trauma Surgery"
    CARDIOLOGY = "Cardiology"
    GENERAL = "General Practice"
    ORTHOPEDIC = "Orthopedic Surgery"

class Doctor:
    def __init__(self, id: str, name: str, specialty: DoctorSpecialty, available: bool = True):
        self.id = id
        self.name = name
        self.specialty = specialty
        self.available = available
        self.current_patient = None
        self.treatment_time_remaining = 0
    
    def assign_patient(self, patient_id: str, treatment_time: int):
        """Assign a patient to this doctor"""
        self.available = False
        self.current_patient = patient_id
        self.treatment_time_remaining = treatment_time
    
    def update_availability(self):
        """Update doctor availability based on treatment time"""
        if self.treatment_time_remaining > 0:
            self.treatment_time_remaining -= 1
        elif not self.available:
            self.available = True
            self.current_patient = None
    
    def __str__(self):
        status = "Available" if self.available else f"Busy (Patient: {self.current_patient})"
        return f"Dr. {self.name} ({self.specialty.value}) - {status}"

class Hospital:
    def __init__(self, id: str, name: str, location: str, capacity: int, gps_coordinates: Tuple[float, float] = None):
        self.id = id
        self.name = name
        self.location = location
        self.capacity = capacity
        self.current_patients = 0
        self.doctors: Dict[str, Doctor] = {}
        self.waiting_list: List[Tuple[str, PatientSeverity]] = []
        self.specialties_required: Dict[DoctorSpecialty, int] = {}
        self.gps_coordinates = gps_coordinates  # (latitude, longitude)
    
    def add_doctor(self, doctor: Doctor):
        """Add a doctor to this hospital"""
        self.doctors[doctor.id] = doctor
        self.specialties_required[doctor.specialty] = self.specialties_required.get(doctor.specialty, 0) + 1
    
    def get_available_doctors(self, specialty: Optional[DoctorSpecialty] = None) -> List[Doctor]:
        """Get list of available doctors, optionally filtered by specialty"""
        available = []
        for doctor in self.doctors.values():
            if doctor.available:
                if specialty is None or doctor.specialty == specialty:
                    available.append(doctor)
        return available
    
    def can_accept_patient(self, severity: PatientSeverity) -> bool:
        """Check if hospital can accept a new patient"""
        if self.current_patients >= self.capacity:
            return False
        
        # For critical patients, ensure at least one emergency doctor is available
        if severity == PatientSeverity.CRITICAL:
            emergency_doctors = self.get_available_doctors(DoctorSpecialty.EMERGENCY)
            trauma_doctors = self.get_available_doctors(DoctorSpecialty.TRAUMA)
            return len(emergency_doctors) > 0 or len(trauma_doctors) > 0
        
        return True
    
    def assign_patient_to_doctor(self, patient_id: str, severity: PatientSeverity) -> Optional[Doctor]:
        """Assign patient to appropriate available doctor"""
        preferred_specialties = self._get_required_specialties(severity)
        
        for specialty in preferred_specialties:
            available_doctors = self.get_available_doctors(specialty)
            if available_doctors:
                doctor = available_doctors[0]  # Assign to first available
                treatment_time = self._get_treatment_time(severity)
                doctor.assign_patient(patient_id, treatment_time)
                self.current_patients += 1
                return doctor
        
        return None
    
    def _get_required_specialties(self, severity: PatientSeverity) -> List[DoctorSpecialty]:
        """Get required doctor specialties based on patient severity"""
        if severity == PatientSeverity.CRITICAL:
            return [DoctorSpecialty.EMERGENCY, DoctorSpecialty.TRAUMA]
        elif severity == PatientSeverity.URGENT:
            return [DoctorSpecialty.EMERGENCY, DoctorSpecialty.GENERAL]
        elif severity == PatientSeverity.MODERATE:
            return [DoctorSpecialty.GENERAL, DoctorSpecialty.ORTHOPEDIC]
        else:  # MILD
            return [DoctorSpecialty.GENERAL]
    
    def _get_treatment_time(self, severity: PatientSeverity) -> int:
        """Get estimated treatment time based on severity"""
        # Treatment time in simulation steps (each step = 1 minute)
        if severity == PatientSeverity.CRITICAL:
            return 120  # 2 hours
        elif severity == PatientSeverity.URGENT:
            return 60   # 1 hour
        elif severity == PatientSeverity.MODERATE:
            return 30   # 30 minutes
        else:  # MILD
            return 15   # 15 minutes
    
    def update_all_doctors(self):
        """Update availability of all doctors"""
        for doctor in self.doctors.values():
            doctor.update_availability()
    
    def __str__(self):
        available_doctors = len(self.get_available_doctors())
        return f"{self.name} ({self.location}) - {self.current_patients}/{self.capacity} patients, {available_doctors} doctors available"
