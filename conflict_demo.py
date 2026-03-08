#!/usr/bin/env python3
"""
Demo of doctor availability conflicts and resolution system
"""

from src.graph import Graph
from src.hospital import Hospital, Doctor, DoctorSpecialty, PatientSeverity, HospitalSystem
from src.ui import InteractiveUI, ISSCalculator, HospitalRanker, Colors
import time


def create_conflict_scenario():
    """Create a scenario with doctor availability conflicts"""
    print(Colors.RED + Colors.BOLD + "⚠️  DOCTOR AVAILABILITY CONFLICT SCENARIO" + Colors.END)
    print(Colors.BLUE + "=" * 60 + Colors.END)
    print()
    
    # Build city
    city = build_demo_city()
    
    # Create hospital system with intentional conflicts
    hospital_system = create_conflict_hospital_system()
    
    print(Colors.YELLOW + "📋 CONFLICT SCENARIO SETUP:" + Colors.END)
    print("• Multiple critical patients arriving simultaneously")
    print("• Limited emergency doctors available")
    print("• Hospitals at different capacity levels")
    print("• Traffic conditions affecting route choices")
    print()
    
    # Show initial hospital status
    print(Colors.CYAN + "🏥 INITIAL HOSPITAL STATUS:" + Colors.END)
    display_hospital_conflicts(hospital_system)
    print()
    
    # Create conflicting patient scenarios
    conflicting_patients = [
        ("E", 6, "Fatal trauma - Highway accident"),
        ("B", 5, "Critical - Heart attack"),
        ("D", 5, "Critical - Stroke symptoms"),
        ("A", 4, "Severe - Multiple injuries")
    ]
    
    print(Colors.RED + "🚨 SIMULTANEOUS EMERGENCY SCENARIOS:" + Colors.END)
    print(Colors.BLUE + "─" * 50 + Colors.END)
    
    for i, (location, iss_score, description) in enumerate(conflicting_patients, 1):
        desc, severity = ISSCalculator.get_iss_description(iss_score)
        severity_color = {
            PatientSeverity.CRITICAL: Colors.RED,
            PatientSeverity.URGENT: Colors.YELLOW,
            PatientSeverity.MODERATE: Colors.BLUE,
            PatientSeverity.MILD: Colors.GREEN
        }.get(severity, Colors.WHITE)
        
        print(f"{i}. Location {location}: {description}")
        print(f"   ISS {iss_score}: {severity_color}{severity.name}{Colors.END}")
        print()
    
    print(Colors.YELLOW + "⚡ PROCESSING CONFLICTS..." + Colors.END)
    print(Colors.BLUE + "─" * 30 + Colors.END)
    
    # Process each patient and show conflicts
    processed_patients = []
    for i, (location, iss_score, description) in enumerate(conflicting_patients, 1):
        print(f"\n{Colors.GREEN}Processing Patient {i}: {description}{Colors.END}")
        
        severity = ISSCalculator.get_iss_description(iss_score)[1]
        
        # Get hospital rankings
        rankings = HospitalRanker.rank_hospitals(
            location, severity, hospital_system, city
        )
        
        if rankings:
            # Try to assign to best hospital
            hospital, total_time, doctor_info = rankings[0]
            
            # Check for doctor availability conflicts
            conflict = check_doctor_conflict(hospital, severity, doctor_info)
            
            if conflict:
                print(f"   {Colors.RED}⚠️  CONFLICT: {conflict}{Colors.END}")
                
                # Try to resolve conflict
                resolved_hospital = resolve_conflict(
                    hospital_system, location, severity, rankings, city
                )
                
                if resolved_hospital:
                    print(f"   {Colors.GREEN}✅ RESOLVED: Assigned to {resolved_hospital.name}{Colors.END}")
                    assign_patient_to_hospital(resolved_hospital, location, severity)
                    processed_patients.append((location, resolved_hospital, severity))
                else:
                    print(f"   {Colors.RED}❌ NO RESOLUTION: No suitable hospital available{Colors.END}")
            else:
                print(f"   {Colors.GREEN}✅ ASSIGNED: {hospital.name} (No conflict){Colors.END}")
                assign_patient_to_hospital(hospital, location, severity)
                processed_patients.append((location, hospital, severity))
        else:
            print(f"   {Colors.RED}❌ NO HOSPITALS AVAILABLE{Colors.END}")
    
    # Show final status
    print(f"\n{Colors.CYAN}📊 FINAL HOSPITAL STATUS AFTER CONFLICT RESOLUTION:{Colors.END}")
    display_hospital_conflicts(hospital_system)
    
    print(f"\n{Colors.GREEN}📋 PATIENT ASSIGNMENT SUMMARY:{Colors.END}")
    print(Colors.BLUE + "─" * 40 + Colors.END)
    for location, hospital, severity in processed_patients:
        print(f"Location {location} → {hospital.name} ({severity.name})")
    
    return hospital_system, city


def create_conflict_hospital_system():
    """Create hospital system with intentional doctor shortages"""
    hospital_system = HospitalSystem()
    
    # Hospital 1: Full capacity, limited emergency doctors
    hospital1 = Hospital("H1", "City General Hospital", "C", capacity=30)
    hospital1.add_doctor(Doctor("D1", "Dr. Smith", DoctorSpecialty.EMERGENCY, available=False))  # Busy
    hospital1.add_doctor(Doctor("D2", "Dr. Johnson", DoctorSpecialty.TRAUMA, available=False))  # Busy
    hospital1.add_doctor(Doctor("D3", "Dr. Williams", DoctorSpecialty.GENERAL))  # Available
    
    # Hospital 2: Medium capacity, one emergency doctor
    hospital2 = Hospital("H2", "St. Mary's Medical Center", "E", capacity=20)
    hospital2.add_doctor(Doctor("D4", "Dr. Brown", DoctorSpecialty.EMERGENCY))  # Available
    hospital2.add_doctor(Doctor("D5", "Dr. Davis", DoctorSpecialty.GENERAL))  # Available
    
    # Hospital 3: Small capacity, no emergency doctors
    hospital3 = Hospital("H3", "Emergency Care Unit", "A", capacity=10)
    hospital3.add_doctor(Doctor("D6", "Dr. Miller", DoctorSpecialty.GENERAL))  # Available
    hospital3.add_doctor(Doctor("D7", "Dr. Wilson", DoctorSpecialty.ORTHOPEDIC))  # Available
    
    hospital_system.add_hospital(hospital1)
    hospital_system.add_hospital(hospital2)
    hospital_system.add_hospital(hospital3)
    
    return hospital_system


def check_doctor_conflict(hospital, severity, doctor_info):
    """Check if there's a doctor availability conflict"""
    if not doctor_info['specialties']:
        return "No doctors available at this hospital"
    
    # Check if required specialty is available
    required_specialties = {
        PatientSeverity.CRITICAL: [DoctorSpecialty.EMERGENCY, DoctorSpecialty.TRAUMA],
        PatientSeverity.URGENT: [DoctorSpecialty.EMERGENCY, DoctorSpecialty.GENERAL],
        PatientSeverity.MODERATE: [DoctorSpecialty.GENERAL, DoctorSpecialty.ORTHOPEDIC],
        PatientSeverity.MILD: [DoctorSpecialty.GENERAL]
    }.get(severity, [])
    
    available_specialties = doctor_info['specialties']
    
    # Check if any required specialty is available
    for req_specialty in required_specialties:
        if req_specialty in available_specialties:
            return None  # No conflict
    
    return f"No doctor with required specialty available (Need: {', '.join(s.value.split()[0] for s in required_specialties)})"


def resolve_conflict(hospital_system, location, severity, rankings, city):
    """Resolve doctor availability conflict by finding alternative hospital"""
    print(f"   {Colors.YELLOW}🔄 Attempting conflict resolution...{Colors.END}")
    
    # Try other hospitals in ranking
    for i, (hospital, total_time, doctor_info) in enumerate(rankings[1:], 1):
        conflict = check_doctor_conflict(hospital, severity, doctor_info)
        
        if not conflict:
            print(f"   {Colors.GREEN}✅ Alternative found: {hospital.name} (Rank {i+1}){Colors.END}")
            return hospital
        else:
            print(f"   {Colors.YELLOW}⚠️  {hospital.name} (Rank {i+1}): {conflict}{Colors.END}")
    
    # If no hospital in rankings works, try all hospitals
    print(f"   {Colors.YELLOW}🔄 Checking all hospitals for availability...{Colors.END}")
    
    for hospital in hospital_system.hospitals.values():
        if hospital.can_accept_patient(severity):
            available_doctors = hospital.get_available_doctors()
            if available_doctors:
                print(f"   {Colors.GREEN}✅ Emergency option: {hospital.name}{Colors.END}")
                return hospital
    
    return None


def assign_patient_to_hospital(hospital, location, severity):
    """Assign patient to hospital and update availability"""
    # Find appropriate doctor and assign
    available_doctors = hospital.get_available_doctors()
    if available_doctors:
        doctor = available_doctors[0]  # Assign first available
        hospital.assign_patient_to_doctor(f"Patient_{location}", severity)


def display_hospital_conflicts(hospital_system):
    """Display hospital status with conflict indicators"""
    for hospital in hospital_system.hospitals.values():
        available_beds = hospital.get_bed_availability()
        available_doctors = len([d for d in hospital.doctors.values() if d.available])
        total_doctors = len(hospital.doctors)
        
        # Color code based on availability
        if available_beds < 10:
            bed_color = Colors.RED
            bed_status = "CRITICAL"
        elif available_beds < 20:
            bed_color = Colors.YELLOW
            bed_status = "LIMITED"
        else:
            bed_color = Colors.GREEN
            bed_status = "GOOD"
        
        if available_doctors == 0:
            doctor_color = Colors.RED
            doctor_status = "NONE"
        elif available_doctors < total_doctors * 0.5:
            doctor_color = Colors.YELLOW
            doctor_status = "LIMITED"
        else:
            doctor_color = Colors.GREEN
            doctor_status = "GOOD"
        
        print(f"{Colors.BOLD}{hospital.name}{Colors.END}")
        print(f"  📍 Location: {hospital.location}")
        print(f"  🛏️  Beds: {bed_color}{available_beds}/{hospital.capacity} ({bed_status}){Colors.END}")
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

    # Set challenging traffic conditions
    city.set_traffic_density("A", "B", 2.0)  # Heavy
    city.set_traffic_density("B", "C", 1.8)  # Heavy
    city.set_traffic_density("A", "D", 0.9)  # Light
    city.set_traffic_density("D", "C", 1.5)  # Moderate
    city.set_traffic_density("C", "E", 2.2)  # Heavy
    city.set_traffic_density("B", "E", 1.3)  # Moderate

    current_time = time.time()
    city.add_traffic_signal("A", "B", {
        'cycle_time': 60, 'green_time': 30, 'current_phase': 'red', 'phase_start': current_time
    })
    city.add_traffic_signal("C", "E", {
        'cycle_time': 90, 'green_time': 45, 'current_phase': 'red', 'phase_start': current_time
    })

    return city


def main():
    """Main conflict demonstration"""
    ui = InteractiveUI()
    ui.clear_screen()
    ui.display_header()
    
    # Run conflict scenario
    hospital_system, city = create_conflict_scenario()
    
    print(Colors.GREEN + "\n✅ CONFLICT DEMONSTRATION COMPLETE" + Colors.END)
    print(Colors.BLUE + "─" * 40 + Colors.END)
    print("Key conflicts demonstrated:")
    print("• Doctor shortage for critical patients")
    print("• Hospital capacity limitations")
    print("• Specialty availability conflicts")
    print("• Automatic conflict resolution")
    print("• Alternative hospital assignment")
    print()
    
    print(Colors.YELLOW + "🚀 To test interactive conflict resolution:" + Colors.END)
    print("   python run_interactive.py")
    print()
    print(Colors.CYAN + "📊 To run again:" + Colors.END)
    print("   python conflict_demo.py")


if __name__ == "__main__":
    main()
