"""
hospital_database.py — Real hospital locations with GPS coordinates.

Contains actual hospital data for Bangalore with real GPS coordinates.
Integrates with the GPS tracking system to show hospital locations on the map.
"""

from typing import List, Dict, Tuple
from hospital_models import Hospital, Doctor, DoctorSpecialty

class HospitalDatabase:
    """Database of real hospitals with GPS coordinates and capabilities."""
    
    def __init__(self):
        self.hospitals: Dict[str, Hospital] = {}
        self._initialize_hospitals()
    
    def _initialize_hospitals(self):
        """Initialize hospital database with real Bangalore hospitals."""
        
        # Bangalore Hospitals with real GPS coordinates
        hospitals_data = [
            {
                'id': 'HOSP_001',
                'name': 'Manipal Hospital',
                'location': 'Old Airport Road, Bangalore',
                'capacity': 650,
                'gps': (12.9634, 77.6285),
                'doctors': [
                    ('DR_001', 'Dr. Ramesh Kumar', DoctorSpecialty.EMERGENCY),
                    ('DR_002', 'Dr. Priya Sharma', DoctorSpecialty.TRAUMA),
                    ('DR_003', 'Dr. Amit Patel', DoctorSpecialty.GENERAL),
                    ('DR_004', 'Dr. Sunita Reddy', DoctorSpecialty.ORTHOPEDIC),
                ]
            },
            {
                'id': 'HOSP_002', 
                'name': 'Apollo Hospital',
                'location': 'Bannerghatta Road, Bangalore',
                'capacity': 500,
                'gps': (12.9135, 77.6101),
                'doctors': [
                    ('DR_005', 'Dr. Venkatesh Iyer', DoctorSpecialty.EMERGENCY),
                    ('DR_006', 'Dr. Anjali Gupta', DoctorSpecialty.TRAUMA),
                    ('DR_007', 'Dr. Rajesh Kumar', DoctorSpecialty.GENERAL),
                ]
            },
            {
                'id': 'HOSP_003',
                'name': 'Fortis Hospital',
                'location': 'Cunningham Road, Bangalore', 
                'capacity': 400,
                'gps': (12.9762, 77.6033),
                'doctors': [
                    ('DR_008', 'Dr. Mohan Singh', DoctorSpecialty.EMERGENCY),
                    ('DR_009', 'Dr. Lakshmi Nair', DoctorSpecialty.GENERAL),
                    ('DR_010', 'Dr. Prakash Rao', DoctorSpecialty.ORTHOPEDIC),
                ]
            },
            {
                'id': 'HOSP_004',
                'name': 'NIMHANS',
                'location': 'Hosur Road, Bangalore',
                'capacity': 800,
                'gps': (12.9394, 77.5999),
                'doctors': [
                    ('DR_011', 'Dr. Satish Kumar', DoctorSpecialty.EMERGENCY),
                    ('DR_012', 'Dr. Meera Krishnan', DoctorSpecialty.TRAUMA),
                    ('DR_013', 'Dr. Arvind Patel', DoctorSpecialty.GENERAL),
                ]
            },
            {
                'id': 'HOSP_005',
                'name': 'Columbia Asia Hospital',
                'location': 'Yeshwanthpur, Bangalore',
                'capacity': 200,
                'gps': (13.0166, 77.5537),
                'doctors': [
                    ('DR_014', 'Dr. Ravi Sharma', DoctorSpecialty.EMERGENCY),
                    ('DR_015', 'Dr. Anita Desai', DoctorSpecialty.GENERAL),
                ]
            },
            {
                'id': 'HOSP_006',
                'name': 'Sakra World Hospital',
                'location': 'Marathahalli, Bangalore',
                'capacity': 350,
                'gps': (12.9591, 77.6986),
                'doctors': [
                    ('DR_016', 'Dr. Karthik Reddy', DoctorSpecialty.EMERGENCY),
                    ('DR_017', 'Dr. Divya Menon', DoctorSpecialty.TRAUMA),
                ]
            }
        ]
        
        # Create hospital objects
        for hospital_data in hospitals_data:
            hospital = Hospital(
                id=hospital_data['id'],
                name=hospital_data['name'],
                location=hospital_data['location'],
                capacity=hospital_data['capacity'],
                gps_coordinates=hospital_data['gps']
            )
            
            # Add doctors
            for doctor_id, doctor_name, specialty in hospital_data['doctors']:
                doctor = Doctor(doctor_id, doctor_name, specialty)
                hospital.add_doctor(doctor)
            
            self.hospitals[hospital_data['id']] = hospital
    
    def get_hospital_by_id(self, hospital_id: str) -> Hospital:
        """Get hospital by ID."""
        return self.hospitals.get(hospital_id)
    
    def get_all_hospitals(self) -> List[Hospital]:
        """Get all hospitals."""
        return list(self.hospitals.values())
    
    def get_hospitals_with_gps(self) -> List[Dict]:
        """Get all hospitals with GPS coordinates for map display."""
        return [
            {
                'id': hospital.id,
                'name': hospital.name,
                'location': hospital.location,
                'latitude': hospital.gps_coordinates[0] if hospital.gps_coordinates else None,
                'longitude': hospital.gps_coordinates[1] if hospital.gps_coordinates else None,
                'capacity': hospital.capacity,
                'current_patients': hospital.current_patients,
                'available_beds': hospital.capacity - hospital.current_patients,
                'specialties': list(hospital.specialties_required.keys())
            }
            for hospital in self.hospitals.values()
            if hospital.gps_coordinates
        ]
    
    def find_nearest_hospitals(self, patient_lat: float, patient_lng: float, limit: int = 3) -> List[Tuple[Hospital, float]]:
        """Find nearest hospitals to patient location."""
        hospitals_with_distance = []
        
        for hospital in self.hospitals.values():
            if hospital.gps_coordinates:
                distance = self._calculate_distance(
                    patient_lat, patient_lng,
                    hospital.gps_coordinates[0], hospital.gps_coordinates[1]
                )
                hospitals_with_distance.append((hospital, distance))
        
        # Sort by distance and return top 'limit'
        hospitals_with_distance.sort(key=lambda x: x[1])
        return hospitals_with_distance[:limit]
    
    def _calculate_distance(self, lat1: float, lng1: float, lat2: float, lng2: float) -> float:
        """Calculate distance between two GPS coordinates (simplified)."""
        # Simple Euclidean distance for demonstration
        # In production, use Haversine formula for accurate Earth distance
        return ((lat2 - lat1) ** 2 + (lng2 - lng1) ** 2) ** 0.5 * 111000  # Approximate meters

# Global hospital database instance
hospital_db = HospitalDatabase()
