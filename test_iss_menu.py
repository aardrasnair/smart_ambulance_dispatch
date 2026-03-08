#!/usr/bin/env python3
"""
Test the new simplified ISS menu display
"""

from src.ui import InteractiveUI, ISSCalculator, Colors

def test_iss_menu():
    """Test the simplified ISS menu display"""
    ui = InteractiveUI()
    ui.clear_screen()
    ui.display_header()
    
    print(Colors.GREEN + "🎯 SIMPLIFIED ISS (0-6) CLASSIFICATION SYSTEM" + Colors.END)
    print()
    
    # Display the new scale
    ISSCalculator.display_iss_scale()
    
    print(Colors.YELLOW + "\n📋 USER INTERFACE DEMO:" + Colors.END)
    print("When users select emergency dispatch, they will see:")
    print()
    
    print(Colors.CYAN + "🏥 INJURY SEVERITY SCORE (ISS 0-6)" + Colors.END)
    print(Colors.BLUE + "─" * 40 + Colors.END)
    print("0: Minimal - First aid only")
    print("1: Minor - Basic treatment") 
    print("2: Moderate - Medical care needed")
    print("3: Serious - Significant injury")
    print("4: Severe - Major injury")
    print("5: Critical - Life threatening")
    print("6: Fatal - Immediate death expected")
    print(Colors.BLUE + "─" * 40 + Colors.END)
    print()
    
    print(Colors.GREEN + "✅ Benefits of the 0-6 Scale:" + Colors.END)
    print("• " + Colors.BOLD + "Simple and intuitive" + Colors.END + " - Easy for non-medical users")
    print("• " + Colors.BOLD + "Quick selection" + Colors.END + " - No complex calculations needed")
    print("• " + Colors.BOLD + "Clear descriptions" + Colors.END + " - Each level has a short, clear meaning")
    print("• " + Colors.BOLD + "Color-coded" + Colors.END + " - Visual severity indicators")
    print("• " + Colors.BOLD + "Medical mapping" + Colors.END + " - Maps to hospital triage levels")
    print()
    
    print(Colors.BLUE + "🚀 To test the interactive system:" + Colors.END)
    print("   python interactive_main.py")
    print()
    print(Colors.CYAN + "📊 To see full demonstration:" + Colors.END)
    print("   python demo_interactive.py")

if __name__ == "__main__":
    test_iss_menu()
