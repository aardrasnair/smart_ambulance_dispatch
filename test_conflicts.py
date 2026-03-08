#!/usr/bin/env python3
"""
Test conflict scenarios with limited doctors
"""

from src.graph import Graph
from src.hospital import Hospital, Doctor, DoctorSpecialty, PatientSeverity, HospitalSystem
from src.ui import InteractiveUI, ISSCalculator, HospitalRanker, Colors
from src.dispatch import check_doctor_conflict, resolve_conflict
import time


def create_limited_doctor_scenario():
    """Create scenario with limited emergency doctors"""
    print(Colors.RED + Colors.BOLD + "⚠️  LIMITED DOCTOR AVAILABILITY TEST" + Colors.END)
    print(Colors.BLUE + "=" * 60 + Colors.END)
    print()
    
    # Build city
    city = build_demo_city()
    
    # Create hospital system with limited emergency doctors
    hospital_system = HospitalSystem()
    
    # Hospital 1: No emergency doctors available
    hospital1 = Hospital("H1", "City General Hospital", "C", capacity=50)
    hospital1.add_doctor(Doctor("D1", "Dr. Smith", DoctorSpecialty.GENERAL))  # Available
    hospital1.add_doctor(Doctor("D2", "Dr. Johnson", DoctorSpecialty.TRAUMA, available=False))  # Busy
    hospital1.add_doctor(Doctor("D3", "Dr. Williams", DoctorSpecialty.ORTHOPEDIC))  # Available
    
    # Hospital 2: One emergency doctor
    hospital2 = Hospital("H2", "St. Mary's Medical Center", "E", capacity=30)
    hospital2.add_doctor(Doctor("D4", "Dr. Brown", DoctorSpecialty.EMERGENCY))  # Available
    hospital2.add_doctor(Doctor("D5", "Dr. Davis", DoctorSpecialty.GENERAL))  # Available
    
    # Hospital 3: No emergency doctors
    hospital3 = Hospital("H3", "Emergency Care Unit", "A", capacity=20)
    hospital3.add_doctor(Doctor("D6", "Dr. Miller", DoctorSpecialty.GENERAL))  # Available
    hospital3.add_doctor(Doctor("D7", "Dr. Wilson", DoctorSpecialty.ORTHOPEDIC))  # Available
    
    hospital_system.add_hospital(hospital1)
    hospital_system.add_hospital(hospital2)
    hospital_system.add_hospital(hospital3)
    
    print(Colors.YELLOW + "📋 SCENARIO: Limited Emergency Doctors" + Colors.END)
    print("• City General: No emergency doctors available")
    print("• St. Mary's: 1 emergency doctor available")
    print("• Emergency Care Unit: No emergency doctors available")
    print()
    
    # Show initial status
    print(Colors.CYAN + "🏥 INITIAL HOSPITAL STATUS:" + Colors.END)
    display_hospital_status(hospital_system)
    print()
    
    # Test critical patient scenarios
    test_critical_patients(city, hospital_system)
    
    return hospital_system, city


def test_critical_patients(city, hospital_system):
    """Test critical patient assignments with conflicts"""
    print(Colors.RED + "🚨 TESTING CRITICAL PATIENT ASSIGNMENTS" + Colors.END)
    print(Colors.BLUE + "─" * 50 + Colors.END)
    
    critical_patients = [
        ("C", 6, "Fatal trauma - Multiple casualties"),
        ("E", 5, "Critical heart attack"),
        ("A", 5, "Critical stroke symptoms"),
    ]
    
    for i, (location, iss_score, description) in enumerate(critical_patients, 1):
        print(f"\n{Colors.GREEN}Test {i}: {description}{Colors.END}")
        print(f"Location: {location}, ISS: {iss_score}")
        
        severity = ISSCalculator.get_iss_description(iss_score)[1]
        
        # Get hospital rankings
        rankings = HospitalRanker.rank_hospitals(
            location, severity, hospital_system, city
        )
        
        if rankings:
            # Test best hospital
            hospital, total_time, doctor_info = rankings[0]
            print(f"Best hospital: {hospital.name} (Time: {total_time:.1f})")
            
            # Check for conflict
            conflict = check_doctor_conflict(hospital, severity)
            
            if conflict:
                print(f"{Colors.RED}⚠️  CONFLICT: {conflict}{Colors.END}")
                
                # Try resolution
                resolved_hospital, resolution_info = resolve_conflict(
                    hospital_system, location, severity, rankings
                )
                
                if resolved_hospital:
                    print(f"{Colors.GREEN}✅ RESOLVED: {resolution_info}{Colors.END}")
                    print(f"Final assignment: {resolved_hospital.name}")
                    
                    # Update hospital (assign doctor)
                    resolved_hospital.assign_patient_to_doctor(f"Test_Patient_{location}", severity)
                else:
                    print(f"{Colors.RED}❌ NO RESOLUTION: {resolution_info}{Colors.END}")
            else:
                print(f"{Colors.GREEN}✅ NO CONFLICT: Direct assignment to {hospital.name}{Colors.END}")
                hospital.assign_patient_to_doctor(f"Test_Patient_{location}", severity)
        else:
            print(f"{Colors.RED}❌ NO HOSPITALS AVAILABLE{Colors.END}")
    
    print()
    print(Colors.CYAN + "📊 FINAL HOSPITAL STATUS:" + Colors.END)
    display_hospital_status(hospital_system)


def display_hospital_status(hospital_system):
    """Display hospital status with conflict indicators"""
    for hospital in hospital_system.hospitals.values():
        available_beds = hospital.get_bed_availability()
        available_doctors = len([d for d in hospital.doctors.values() if d.available])
        total_doctors = len(hospital.doctors)
        
        # Color code based on availability
        if available_doctors == 0:
            doctor_color = Colors.RED
            doctor_status = "CRITICAL"
        elif available_doctors < total_doctors * 0.5:
            doctor_color = Colors.YELLOW
            doctor_status = "LIMITED"
        else:
            doctor_color = Colors.GREEN
            doctor_status = "GOOD"
        
        print(f"{Colors.BOLD}{hospital.name}{Colors.END}")
        print(f"  📍 Location: {hospital.location}")
        print(f"  🛏️  Beds: {available_beds}/{hospital.capacity}")
        print(f"  👨‍⚕️  Doctors: {doctor_color}{available_doctors}/{total_doctors} ({doctor_status}){Colors.END}")
        
        # Show doctor details
        doctor_details = []
        for doctor in hospital.doctors.values():
            status = "✅" if doctor.available else "❌"
            specialty = doctor.specialty.value.split()[0]
            doctor_details.append(f"{specialty}:{status}")
        
        print(f"  📋 Staff: {', '.join(doctor_details)}")
        print()


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

    # Set normal traffic conditions
    city.set_traffic_density("A", "B", 1.0)
    city.set_traffic_density("B", "C", 1.0)
    city.set_traffic_density("A", "D", 1.0)
    city.set_traffic_density("D", "C", 1.0)
    city.set_traffic_density("C", "E", 1.0)
    city.set_traffic_density("B", "E", 1.0)

    return city


def main():
    """Main test function"""
    ui = InteractiveUI()
    ui.clear_screen()
    ui.display_header()
    
    # Run limited doctor scenario
    create_limited_doctor_scenario()
    
    print(Colors.GREEN + "\n✅ CONFLICT TEST COMPLETE" + Colors.END)
    print(Colors.BLUE + "─" * 40 + Colors.END)
    print("Key conflicts tested:")
    print("• No emergency doctors available")
    print("• Automatic conflict detection")
    print("• Alternative hospital assignment")
    print("• Priority-based resolution")
    print()
    
    print(Colors.YELLOW + "🚀 To test interactively:" + Colors.END)
    print("   python run_interactive.py")
    print()
    print(Colors.CYAN + "📊 To run full conflict demo:" + Colors.END)
    print("   python conflict_demo.py")


if __name__ == "__main__":
    main()
