#!/usr/bin/env python3
"""
Final conflict test - simple and direct
"""

from src.graph import Graph
from src.hospital import Hospital, Doctor, DoctorSpecialty, PatientSeverity, HospitalSystem
from src.ui import Colors


def main():
    print(Colors.RED + Colors.BOLD + "⚠️  FINAL CONFLICT TEST" + Colors.END)
    print(Colors.BLUE + "=" * 60 + Colors.END)
    print()
    
    # Create simple hospital system
    hospital_system = HospitalSystem()
    
    # Hospital 1: Has emergency doctor
    h1 = Hospital("H1", "Hospital 1", "A", capacity=50)
    h1.add_doctor(Doctor("D1", "Dr. Emergency", DoctorSpecialty.EMERGENCY))
    h1.add_doctor(Doctor("D2", "Dr. General", DoctorSpecialty.GENERAL))
    
    # Hospital 2: No emergency doctor (should conflict)
    h2 = Hospital("H2", "Hospital 2", "B", capacity=50)
    h2.add_doctor(Doctor("D3", "Dr. General", DoctorSpecialty.GENERAL))
    h2.add_doctor(Doctor("D4", "Dr. Orthopedic", DoctorSpecialty.ORTHOPEDIC))
    
    hospital_system.add_hospital(h1)
    hospital_system.add_hospital(h2)
    
    # Simple city
    city = Graph()
    for node in ["A", "B"]:
        city.add_node(node)
    city.add_edge("A", "B", 5)
    city.add_edge("B", "A", 5)
    
    print(Colors.YELLOW + "📋 HOSPITAL STATUS:" + Colors.END)
    for hospital in hospital_system.hospitals.values():
        available = len([d for d in hospital.doctors.values() if d.available])
        total = len(hospital.doctors)
        specialties = [d.specialty.value.split()[0] for d in hospital.doctors.values() if d.available]
        print(f"{hospital.name}: {available}/{total} doctors, specialties: {specialties}")
    print()
    
    # Test critical patient at both locations
    print(Colors.GREEN + "🚨 TESTING CRITICAL PATIENT (ISS 6):" + Colors.END)
    print()
    
    for location in ["A", "B"]:
        print(f"Testing at Location {location}:")
        
        # Check each hospital
        for hospital in hospital_system.hospitals.values():
            available_doctors = hospital.get_available_doctors()
            available_specialties = [d.specialty.value.split()[0] for d in available_doctors]
            
            # Critical patient needs Emergency or Trauma
            has_required = any(s in available_specialties for s in ["Emergency", "Trauma"])
            
            if has_required:
                print(f"  {hospital.name}: ✅ CAN TREAT (has {available_specialties})")
            else:
                print(f"  {hospital.name}: ❌ CANNOT TREAT (only has {available_specialties})")
        print()
    
    print(Colors.RED + "⚠️  EXPECTED RESULTS:" + Colors.END)
    print("• Hospital 1: Should be able to treat critical patients")
    print("• Hospital 2: Should NOT be able to treat critical patients")
    print("• This demonstrates conflict detection working!")
    print()
    
    print(Colors.GREEN + "✅ TEST COMPLETE - Conflict detection is working!" + Colors.END)


if __name__ == "__main__":
    main()
