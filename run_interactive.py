#!/usr/bin/env python3
"""
Simple interactive test that stays open for user interaction
"""

from src.ui import InteractiveUI, ISSCalculator, Colors
from src.hospital import Hospital, Doctor, DoctorSpecialty, PatientSeverity, HospitalSystem
from src.graph import Graph
import time

def run_interactive_test():
    """Run interactive system with manual control"""
    ui = InteractiveUI()
    
    # Initialize system
    city = build_demo_city()
    hospital_system = build_demo_hospital_system()
    
    while True:
        try:
            ui.clear_screen()
            ui.display_header()
            
            print(Colors.GREEN + "🚑 SMART AMBULANCE DISPATCH - INTERACTIVE TEST" + Colors.END)
            print(Colors.BLUE + "─" * 50 + Colors.END)
            print("1. 🚨 Emergency Dispatch (with ISS 0-6)")
            print("2. 🏥 View Hospital Status")
            print("3. 🚦 View Traffic Conditions")
            print("4. 📋 View ISS Scale")
            print("5. 🚪 Exit")
            print(Colors.BLUE + "─" * 50 + Colors.END)
            
            try:
                choice = int(input("\nSelect option (1-5): "))
                
                if choice == 1:
                    test_emergency_dispatch(ui, city, hospital_system)
                elif choice == 2:
                    ui.clear_screen()
                    ui.display_header()
                    ui.display_hospital_status(hospital_system)
                    input(Colors.YELLOW + "\nPress Enter to continue..." + Colors.END)
                elif choice == 3:
                    ui.clear_screen()
                    ui.display_header()
                    ui.display_traffic_status(city)
                    input(Colors.YELLOW + "\nPress Enter to continue..." + Colors.END)
                elif choice == 4:
                    ui.clear_screen()
                    ui.display_header()
                    ISSCalculator.display_iss_scale()
                    input(Colors.YELLOW + "\nPress Enter to continue..." + Colors.END)
                elif choice == 5:
                    print(Colors.GREEN + "Thank you for testing! Stay safe! 🚑" + Colors.END)
                    break
                else:
                    print(Colors.RED + "Invalid option. Please try again." + Colors.END)
                    time.sleep(2)
                    
            except ValueError:
                print(Colors.RED + "Please enter a valid number." + Colors.END)
                time.sleep(2)
                
        except KeyboardInterrupt:
            print(Colors.GREEN + "\n\nExiting system. Stay safe! 🚑" + Colors.END)
            break
        except Exception as e:
            print(Colors.RED + f"Error: {e}" + Colors.END)
            input(Colors.YELLOW + "Press Enter to continue..." + Colors.END)


def test_emergency_dispatch(ui, city, hospital_system):
    """Test emergency dispatch workflow"""
    ui.clear_screen()
    ui.display_header()
    
    print(Colors.RED + "🚨 EMERGENCY DISPATCH TEST" + Colors.END)
    print(Colors.BLUE + "─" * 40 + Colors.END)
    
    # Get patient location
    locations = list(city.get_nodes())
    print("Available locations:", ", ".join(locations))
    
    try:
        patient_location = input(f"Enter patient location ({', '.join(locations)}): ").upper()
        if patient_location not in locations:
            print(Colors.RED + "Invalid location. Using 'A' as default." + Colors.END)
            patient_location = "A"
    except:
        patient_location = "A"
    
    # Get ISS score
    print(Colors.YELLOW + "\n🏥 INJURY SEVERITY SCORE (ISS 0-6)" + Colors.END)
    print(Colors.BLUE + "─" * 40 + Colors.END)
    print("0: Minimal - First aid only")
    print("1: Minor - Basic treatment") 
    print("2: Moderate - Medical care needed")
    print("3: Serious - Significant injury")
    print("4: Severe - Major injury")
    print("5: Critical - Life threatening")
    print("6: Fatal - Immediate death expected")
    print(Colors.BLUE + "─" * 40 + Colors.END)
    
    try:
        iss_score = int(input("Enter ISS score (0-6): "))
        if not (0 <= iss_score <= 6):
            print(Colors.RED + "Invalid score. Using 2 (Moderate) as default." + Colors.END)
            iss_score = 2
    except:
        iss_score = 2
    
    # Show classification
    desc, severity = ISSCalculator.get_iss_description(iss_score)
    severity_color = {
        PatientSeverity.CRITICAL: Colors.RED,
        PatientSeverity.URGENT: Colors.YELLOW,
        PatientSeverity.MODERATE: Colors.BLUE,
        PatientSeverity.MILD: Colors.GREEN
    }.get(severity, Colors.WHITE)
    
    print(f"\n{Colors.YELLOW}Classification: {severity_color}{severity.name}{Colors.END}")
    print(f"Description: {desc}")
    
    # Find best hospital
    from src.ui import HospitalRanker
    rankings = HospitalRanker.rank_hospitals(
        patient_location, severity, hospital_system, city
    )
    
    if rankings:
        print(f"\n{Colors.GREEN}🏥 RECOMMENDED HOSPITAL:{Colors.END}")
        hospital, total_time, doctor_info = rankings[0]
        print(f"Hospital: {hospital.name}")
        print(f"Location: {hospital.location}")
        print(f"Estimated Time: {total_time:.1f} units")
        print(f"Available Doctors: {doctor_info['count']}")
        if doctor_info['specialties']:
            specialties = ", ".join(s.value.split()[0] for s in doctor_info['specialties'])
            print(f"Specialties: {specialties}")
        
        # Check for conflicts and show resolution
        from src.dispatch import check_doctor_conflict, resolve_conflict
        conflict = check_doctor_conflict(hospital, severity)
        
        if conflict:
            print(f"\n{Colors.RED}⚠️  CONFLICT DETECTED:{Colors.END}")
            print(f"   {conflict}")
            print(f"\n{Colors.YELLOW}🔄 RESOLVING CONFLICT...{Colors.END}")
            
            resolved_hospital, resolution_info = resolve_conflict(
                hospital_system, patient_location, severity, rankings
            )
            
            if resolved_hospital:
                print(f"   {Colors.GREEN}✅ RESOLVED: {resolution_info}{Colors.END}")
                print(f"   Final Assignment: {resolved_hospital.name}")
                
                # Simulate doctor assignment (make doctor busy)
                resolved_hospital.assign_patient_to_doctor(f"Test_Patient_{patient_location}", severity)
            else:
                print(f"   {Colors.RED}❌ NO RESOLUTION: {resolution_info}{Colors.END}")
        else:
            print(f"\n{Colors.GREEN}✅ NO CONFLICTS: Direct assignment possible{Colors.END}")
            
            # Simulate doctor assignment (make doctor busy for next test)
            hospital.assign_patient_to_doctor(f"Test_Patient_{patient_location}", severity)
            
        # Show updated hospital status for debugging
        print(f"\n{Colors.CYAN}📊 UPDATED HOSPITAL STATUS:{Colors.END}")
        print(f"{hospital.name}: Doctors available = {len([d for d in hospital.doctors.values() if d.available])}/{len(hospital.doctors)}")
    else:
        print(Colors.RED + "No suitable hospitals available" + Colors.END)
    
    input(Colors.YELLOW + "\nPress Enter to continue..." + Colors.END)


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

    city.set_traffic_density("A", "B", 1.2)
    city.set_traffic_density("B", "C", 1.8)
    city.set_traffic_density("A", "D", 0.9)
    city.set_traffic_density("D", "C", 1.3)
    city.set_traffic_density("C", "E", 1.6)
    city.set_traffic_density("B", "E", 1.1)

    current_time = time.time()
    city.add_traffic_signal("A", "B", {
        'cycle_time': 60, 'green_time': 30, 'current_phase': 'green', 'phase_start': current_time
    })
    city.add_traffic_signal("C", "E", {
        'cycle_time': 90, 'green_time': 45, 'current_phase': 'red', 'phase_start': current_time
    })

    return city


def build_demo_hospital_system():
    """Build demo hospital system with conflicts"""
    hospital_system = HospitalSystem()
    
    hospital1 = Hospital("H1", "City General Hospital", "C", capacity=50)
    hospital2 = Hospital("H2", "St. Mary's Medical Center", "E", capacity=30)
    hospital3 = Hospital("H3", "Emergency Care Unit", "A", capacity=20)
    
    # Hospital 1: Limited emergency doctors (some busy)
    hospital1.add_doctor(Doctor("D1", "Dr. Smith", DoctorSpecialty.EMERGENCY))
    hospital1.add_doctor(Doctor("D2", "Dr. Johnson", DoctorSpecialty.TRAUMA, available=False))  # Busy
    hospital1.add_doctor(Doctor("D3", "Dr. Williams", DoctorSpecialty.GENERAL))
    
    # Hospital 2: Only one emergency doctor (will get busy)
    hospital2.add_doctor(Doctor("D4", "Dr. Brown", DoctorSpecialty.EMERGENCY))
    hospital2.add_doctor(Doctor("D5", "Dr. Davis", DoctorSpecialty.GENERAL))
    
    # Hospital 3: NO emergency doctors (conflict for critical patients)
    hospital3.add_doctor(Doctor("D6", "Dr. Miller", DoctorSpecialty.GENERAL))
    hospital3.add_doctor(Doctor("D7", "Dr. Wilson", DoctorSpecialty.ORTHOPEDIC))
    
    hospital_system.add_hospital(hospital1)
    hospital_system.add_hospital(hospital2)
    hospital_system.add_hospital(hospital3)
    
    return hospital_system


if __name__ == "__main__":
    run_interactive_test()
