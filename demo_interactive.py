#!/usr/bin/env python3
"""
Demo script to showcase the interactive ambulance dispatch system
"""

from src.graph import Graph
from src.hospital import Hospital, Doctor, DoctorSpecialty, PatientSeverity, HospitalSystem
from src.ui import InteractiveUI, ISSCalculator, HospitalRanker, Colors
import time


def demo_iss_classification():
    """Demonstrate ISS classification system"""
    print(Colors.HEADER + Colors.BOLD)
    print("╔══════════════════════════════════════════════════════════════╗")
    print("║          SMART AMBULANCE DISPATCH SYSTEM v2.0                ║")
    print("║         Real-time Hospital Ranking & Triage System            ║")
    print("╚══════════════════════════════════════════════════════════════╝")
    print(Colors.END)
    
    # Show ISS scale
    ISSCalculator.display_iss_scale()
    
    # Demo different simplified ISS scores
    demo_scores = [6, 5, 4, 3, 2, 1, 0]
    
    print(Colors.CYAN + "\n📋 ISS SCORE DEMONSTRATION" + Colors.END)
    print(Colors.BLUE + "─" * 50 + Colors.END)
    
    for score in demo_scores:
        desc, severity = ISSCalculator.get_iss_description(score)
        severity_color = {
            PatientSeverity.CRITICAL: Colors.RED,
            PatientSeverity.URGENT: Colors.YELLOW,
            PatientSeverity.MODERATE: Colors.BLUE,
            PatientSeverity.MILD: Colors.GREEN
        }.get(severity, Colors.WHITE)
        
        print(f"ISS {score:2d}: {severity_color}{desc}{Colors.END}")
    
    print()


def demo_hospital_ranking():
    """Demonstrate real-time hospital ranking"""
    print(Colors.GREEN + "🏥 HOSPITAL RANKING DEMONSTRATION" + Colors.END)
    print(Colors.BLUE + "─" * 60 + Colors.END)
    
    # Build demo system
    city = build_demo_city()
    hospital_system = build_demo_hospital_system()
    
    # Test different patient scenarios with simplified ISS
    scenarios = [
        ("E", 6, "Fatal injury at location E"),
        ("B", 4, "Severe injury at location B"),
        ("D", 2, "Moderate injury at location D"),
        ("A", 1, "Minor injury at location A")
    ]
    
    for location, iss_score, description in scenarios:
        print(f"\n{Colors.YELLOW}Scenario: {description}{Colors.END}")
        print(f"ISS Score: {iss_score}")
        
        severity = ISSCalculator.get_iss_description(iss_score)[1]
        
        # Get hospital rankings
        rankings = HospitalRanker.rank_hospitals(
            location, severity, hospital_system, city
        )
        
        if rankings:
            print(f"{'Rank':<5} {'Hospital':<25} {'Total Time':<12} {'Travel':<8} {'Processing':<12} {'Doctors':<8}")
            print(Colors.BLUE + "─" * 70 + Colors.END)
            
            for i, (hospital, total_time, doctor_info) in enumerate(rankings, 1):
                # Extract travel and processing time
                travel_time = total_time * 0.4  # Approximate
                processing_time = total_time - travel_time
                
                # Color code based on time
                if total_time < 15:
                    time_color = Colors.GREEN
                elif total_time < 25:
                    time_color = Colors.YELLOW
                else:
                    time_color = Colors.RED
                
                print(f"{i:<5} {hospital.name[:24]:<25} {time_color}{total_time:.1f}{Colors.END:<11} "
                      f"{travel_time:.1f}{'':<8} {processing_time:.1f}{'':<12} {doctor_info['count']:<8}")
                
                # Show doctor specialties
                if doctor_info['specialties']:
                    specialties = ", ".join(s.value.split()[0] for s in doctor_info['specialties'])
                    print(f"      {Colors.CYAN}Available: {specialties}{Colors.END}")
        else:
            print(Colors.RED + "No suitable hospitals available" + Colors.END)
        
        print()


def build_demo_city():
    """Build demo city with traffic and signals"""
    city = Graph()

    nodes = ["A", "B", "C", "D", "E"]
    for node in nodes:
        city.add_node(node)

    # Add roads with base travel times
    city.add_edge("A", "B", 4)
    city.add_edge("B", "C", 3)
    city.add_edge("A", "D", 2)
    city.add_edge("D", "C", 5)
    city.add_edge("C", "E", 6)
    city.add_edge("B", "E", 10)

    # Set traffic densities
    city.set_traffic_density("A", "B", 1.5)
    city.set_traffic_density("B", "C", 2.0)
    city.set_traffic_density("A", "D", 0.8)
    city.set_traffic_density("D", "C", 1.2)
    city.set_traffic_density("C", "E", 1.8)
    city.set_traffic_density("B", "E", 1.1)

    # Add traffic signals
    current_time = time.time()
    city.add_traffic_signal("A", "B", {
        'cycle_time': 60,
        'green_time': 30,
        'current_phase': 'green',
        'phase_start': current_time
    })
    
    city.add_traffic_signal("C", "E", {
        'cycle_time': 90,
        'green_time': 45,
        'current_phase': 'red',
        'phase_start': current_time
    })

    return city


def build_demo_hospital_system():
    """Build demo hospital system"""
    hospital_system = HospitalSystem()
    
    # Create hospitals
    hospital1 = Hospital("H1", "City General Hospital", "C", capacity=50)
    hospital2 = Hospital("H2", "St. Mary's Medical Center", "E", capacity=30)
    hospital3 = Hospital("H3", "Emergency Care Unit", "A", capacity=20)
    
    # Add doctors to Hospital 1
    hospital1.add_doctor(Doctor("D1", "Dr. Smith", DoctorSpecialty.EMERGENCY))
    hospital1.add_doctor(Doctor("D2", "Dr. Johnson", DoctorSpecialty.TRAUMA))
    hospital1.add_doctor(Doctor("D3", "Dr. Williams", DoctorSpecialty.GENERAL))
    
    # Add doctors to Hospital 2
    hospital2.add_doctor(Doctor("D4", "Dr. Brown", DoctorSpecialty.EMERGENCY))
    hospital2.add_doctor(Doctor("D5", "Dr. Davis", DoctorSpecialty.GENERAL))
    
    # Add doctors to Hospital 3
    hospital3.add_doctor(Doctor("D6", "Dr. Miller", DoctorSpecialty.EMERGENCY))
    hospital3.add_doctor(Doctor("D7", "Dr. Wilson", DoctorSpecialty.ORTHOPEDIC))
    
    hospital_system.add_hospital(hospital1)
    hospital_system.add_hospital(hospital2)
    hospital_system.add_hospital(hospital3)
    
    return hospital_system


def demo_hospital_status():
    """Demonstrate hospital status display"""
    print(Colors.CYAN + "🏥 HOSPITAL SYSTEM STATUS" + Colors.END)
    print(Colors.BLUE + "─" * 50 + Colors.END)
    
    hospital_system = build_demo_hospital_system()
    
    for hospital in hospital_system.hospitals.values():
        available_beds = hospital.get_bed_availability()
        available_doctors = len([d for d in hospital.doctors.values() if d.available])
        total_doctors = len(hospital.doctors)
        
        # Color code based on availability
        if available_beds > 20:
            bed_color = Colors.GREEN
        elif available_beds > 10:
            bed_color = Colors.YELLOW
        else:
            bed_color = Colors.RED
        
        if available_doctors > total_doctors * 0.5:
            doctor_color = Colors.GREEN
        elif available_doctors > 0:
            doctor_color = Colors.YELLOW
        else:
            doctor_color = Colors.RED
        
        print(f"\n{Colors.BOLD}{hospital.name}{Colors.END}")
        print(f"  📍 Location: {hospital.location}")
        print(f"  🛏️  Beds: {bed_color}{available_beds}/{hospital.capacity}{Colors.END}")
        print(f"  👨‍⚕️  Doctors: {doctor_color}{available_doctors}/{total_doctors}{Colors.END}")
        
        # Show available doctors by specialty
        available_by_specialty = {}
        for doctor in hospital.doctors.values():
            if doctor.available:
                specialty = doctor.specialty.value.split()[0]
                available_by_specialty[specialty] = available_by_specialty.get(specialty, 0) + 1
        
        if available_by_specialty:
            specialties = ", ".join(f"{k}: {v}" for k, v in available_by_specialty.items())
            print(f"  📋 Available: {specialties}")


def demo_traffic_status():
    """Demonstrate traffic status display"""
    print(Colors.CYAN + "\n🚦 TRAFFIC CONDITIONS" + Colors.END)
    print(Colors.BLUE + "─" * 50 + Colors.END)
    
    city = build_demo_city()
    
    for edge_key, density in city.traffic_density.items():
        from_node, to_node = edge_key
        base_weight = None
        for neighbor, weight in city.graph.get(from_node, []):
            if neighbor == to_node:
                base_weight = weight
                break
        
        if base_weight:
            current_weight = city.get_current_weight(from_node, to_node, base_weight)
            signal = city.traffic_signals.get(edge_key)
            
            # Traffic level color coding
            if density < 1.0:
                traffic_color = Colors.GREEN
                traffic_level = "Light"
            elif density > 1.5:
                traffic_color = Colors.RED
                traffic_level = "Heavy"
            else:
                traffic_color = Colors.YELLOW
                traffic_level = "Normal"
            
            # Signal color coding
            if signal:
                signal_color = Colors.GREEN if signal['current_phase'] == 'green' else Colors.RED
                signal_status = f"{signal_color}Signal: {signal['current_phase'].upper()}{Colors.END}"
            else:
                signal_status = "No signal"
            
            print(f"  {from_node} → {to_node}: {traffic_color}{traffic_level}{Colors.END} "
                  f"(Base: {base_weight}, Current: {current_weight:.1f}) {signal_status}")


def main():
    """Main demo function"""
    demo_iss_classification()
    demo_hospital_status()
    demo_traffic_status()
    demo_hospital_ranking()
    
    print(Colors.GREEN + "\n✅ DEMO COMPLETE" + Colors.END)
    print("To run the interactive system, use: python interactive_main.py")


if __name__ == "__main__":
    main()
