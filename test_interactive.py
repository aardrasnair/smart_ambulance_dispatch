#!/usr/bin/env python3
"""
Quick test of the interactive menu system
"""

from src.ui import InteractiveUI, ISSCalculator, Colors
import time

def test_menu():
    """Test the interactive menu display"""
    ui = InteractiveUI()
    ui.clear_screen()
    ui.display_header()
    
    print(Colors.GREEN + "✅ Interactive System Features Demonstrated:" + Colors.END)
    print()
    
    print("🎯 " + Colors.BOLD + "ISS Classification System" + Colors.END)
    print("   • Converts injury scores (0-75) to severity levels")
    print("   • Provides clear medical descriptions")
    print("   • Color-coded severity indicators")
    print()
    
    print("🏥 " + Colors.BOLD + "Real-time Hospital Ranking" + Colors.END)
    print("   • Ranks hospitals by total response time")
    print("   • Considers traffic conditions and signals")
    print("   • Shows doctor availability by specialty")
    print("   • Color-coded time estimates")
    print()
    
    print("🚦 " + Colors.BOLD + "Traffic Integration" + Colors.END)
    print("   • Real-time traffic density updates")
    print("   • Traffic signal timing considerations")
    print("   • Dynamic route calculations")
    print()
    
    print("🎨 " + Colors.BOLD + "Aesthetic Terminal Display" + Colors.END)
    print("   • Color-coded severity levels")
    print("   • Professional formatting and borders")
    print("   • Emoji icons for visual clarity")
    print("   • Interactive menu navigation")
    print()
    
    print(Colors.CYAN + "📋 Sample Simplified ISS Classifications (0-6):" + Colors.END)
    test_scores = [6, 5, 4, 3, 2, 1, 0]
    
    for score in test_scores:
        desc, severity = ISSCalculator.get_iss_description(score)
        severity_color = {
            'CRITICAL': Colors.RED,
            'URGENT': Colors.YELLOW,
            'MODERATE': Colors.BLUE,
            'MILD': Colors.GREEN
        }.get(severity.name, Colors.WHITE)
        
        print(f"   ISS {score:2d}: {severity_color}{severity.name:8s}{Colors.END} - {desc}")
    
    print()
    print(Colors.YELLOW + "🚀 To run the full interactive system:" + Colors.END)
    print("   python interactive_main.py")
    print()
    print(Colors.BLUE + "📊 To see the complete demonstration:" + Colors.END)
    print("   python demo_interactive.py")

if __name__ == "__main__":
    test_menu()
