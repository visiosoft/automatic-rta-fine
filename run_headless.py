"""
Test script to run automation in different modes
"""
import sys
sys.path.append('.')
from automate_rta import automate_rta_violations

print("=" * 60)
print("Testing RTA Automation in HEADLESS MODE")
print("=" * 60)
print("\nNo browser window should appear!")
print("The automation runs completely in the background.\n")

# Run in headless mode (default)
automate_rta_violations(headless=True)

print("\n" + "=" * 60)
print("HEADLESS MODE TEST COMPLETED")
print("=" * 60)
