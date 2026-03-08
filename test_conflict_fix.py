#!/usr/bin/env python3
"""
Test to verify conflict detection is working
"""

from src.graph import Graph
from src.hospital import Hospital, Doctor, DoctorSpecialty, PatientSeverity, HospitalSystem
from src.ui import InteractiveUI, ISSCalculator, HospitalRanker, Colors
from src.dispatch import check_doctor_conflict, resolve_conflict
import time


def test_conflict_detection():
    """Test conflict detection with proper setup"""
    print(Colors.RED + Colors.BOLD + "⚠️  CONFLICT DETECTION TEST" + Colors.END)
    print(Colors.BLUE + "=" * 60 + Colors.END)
    print()
    
    # Build city
    city = build_demo_city()
    
    # Create hospital system with intentional conflicts
    hospital_system = create_conflict_scenario()
    
    print(Colors.YELLOW + "📋 TESTING CONFLICT SCENARIOS:" + Colors.END)
    print()
    
    # Test Case 1: Critical patient with no emergency doctors
    print(f"{Colors.GREEN}Test 1: Critical patient (ISS 5) at Location E{Colors.END}")
    
    severity = PatientSeverity.CRITICAL
    rankings = HospitalRanker.rank_hospitals("E", severity, hospital_system, city)
    
    if rankings:
        hospital, total_time, doctor_info = rankings[0]
        print(f"Best hospital: {hospital.name}")
        print(f"Available doctors: {doctor_info['count']}")
        
        # Check for conflict
        conflict = check_doctor_conflict(hospital, severity)
        
        if conflict:
            print(f"{Colors.RED}✅ CONFLICT DETECTED: {conflict}{Colors.END}")
            
            # Try resolution
            resolved_hospital, resolution_info = resolve_conflict(
                hospital_system, "E", severity, rankings
            )
            
            if resolved_hospital:
                print(f"{Colors.GREEN}✅ RESOLUTION: {resolution_info}{Colors.END}")
                print(f"Final assignment: {resolved_hospital.name}")
            else:
                print(f"{Colors.RED}❌ NO RESOLUTION: {resolution_info}{Colors.END}")
        else:
            print(f"{Colors.GREEN}❌ NO CONFLICT DETECTED (this is the problem!){Colors.END}")
    else:
        print(f"{Colors.RED}❌ NO HOSPITALS AVAILABLE{Colors.END}")
    
    print()
    
    # Test Case 2: Check hospital 3 (no emergency doctors)
    print(f"{Colors.GREEN}Test 2: Critical patient (ISS 6) - should conflict at Hospital 3{Colors.END}")
    
    hospital3 = hospital_system.hospitals["H3"]  # Emergency Care Unit
    conflict = check_doctor_conflict(hospital3, PatientSeverity.CRITICAL)
    
    if conflict:
        print(f"{Colors.GREEN}✅ CONFLICT DETECTED at Hospital 3: {conflict}{Colors.END}")
    else:
        print(f"{Colors.RED}❌ NO CONFLICT DETECTED at Hospital 3 (this is wrong!){Colors.END}")
    
    print()
    
    # Show all hospital statuses
    print(Colors.CYAN + "📊 ALL HOSPITAL STATUSES:" + Colors.END)
    for hid, hospital in hospital_system.hospitals.items():
        available_doctors = [d for d in hospital.doctors.values() if d.available]
        available_specialties = [d.specialty.value.split()[0] for d in available_doctors]
        
        print(f"{hospital.name}:")
        print(f"  Available doctors: {len(available_doctors)}/{len(hospital.doctors)}")
        print(f"  Available specialties: {available_specialties}")
        
        # Test conflict detection
        conflict = check_doctor_conflict(hospital, PatientSeverity.CRITICAL)
        status = f"{Colors.RED}CONFLICT{Colors.END}" if conflict else f"{Colors.GREEN}NO CONFLICT{Colors.END}"
        print(f"  Critical patient: {status}")
        print()


def create_conflict_scenario():
    """Create hospital system with known conflicts"""
    hospital_system = HospitalSystem()
    
    # Hospital 1: Limited emergency doctors
    hospital1 = Hospital("H1", "City General Hospital", "C", capacity=50)
    hospital1.add_doctor(Doctor("D1", "Dr. Smith", DoctorSpecialty.EMERGENCY))
    hospital1.add_doctor(Doctor("D2", "Dr. Johnson", DoctorSpecialty.TRAUMA, available=False))  # Busy
    hospital1.add_doctor(Doctor("D3", "Dr. Williams", DoctorSpecialty.GENERAL))
    
    # Hospital 2: One emergency doctor
    hospital2 = Hospital("H2", "St. Mary's Medical Center", "E", capacity=30)
    hospital2.add_doctor(Doctor("D4", "Dr. Brown", DoctorSpecialty.EMERGENCY))
    hospital2.add_doctor(Doctor("D5", "Dr. Davis", DoctorSpecialty.GENERAL))
    
    # Hospital 3: No emergency doctors (should always conflict for critical)
    hospital3 = Hospital("H3", "Emergency Care Unit", "A", capacity=20)
    hospital3.add_doctor(Doctor("D6", "Dr. Miller", DoctorSpecialty.GENERAL))
    hospital3.add_doctor(Doctor("D7", "Dr. Wilson", DoctorSpecialty.ORTHOPEDIC))
    
    hospital_system.add_hospital(hospital1)
    hospital_system.add_hospital(hospital2)
    hospital_system.add_hospital(hospital3)
    
    return hospital_system


def build_demo_city():
    """Build demo city"""
    city = Graph()
    nodes = ["A", "B", "C", "D", "E"]
    for node in nodes:
        city.add_node(node)

    city.add_edge("A", "B", 4)
    city.add_edge("B", "C", 3)
    city.add_edge("A", "D", 2)
    city.add_edge("D", "C", 5)
    city.add_edge("C", "E", 6)
    city.add_edge("B", "E", 10)

    city.set_traffic_density("A", "B", 1.0)
    city.set_traffic_density("B", "C", 1.0)
    city.set_traffic_density("A", "D", 1.0)
    city.set_traffic_density("D", "C", 1.0)
    city.set_traffic_density("C", "E", 1.0)
    city.set_traffic_density("B", "E", 1.0)

    return city


def main():
    """Main test function"""
    test_conflict_detection()
    
    print(Colors.GREEN + "\n✅ CONFLICT TEST COMPLETE" + Colors.END)
    print(Colors.BLUE + "─" * 40 + Colors.END)
    print("Expected results:")
    print("• Test 1: Should detect conflict and resolve to alternative hospital")
    print("• Test 2: Should detect conflict at Hospital 3 (no emergency doctors)")
    print()
    print("If conflicts are NOT detected, there's a bug in the system!")


if __name__ == "__main__":
    main()
