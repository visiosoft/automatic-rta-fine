"""
Test script to run automation with visible browser
"""
import sys
sys.path.append('.')
from automate_rta import automate_rta_violations

print("=" * 60)
print("Testing RTA Automation in NORMAL MODE")
print("=" * 60)
print("\nBrowser window WILL appear and you can see the automation.\n")

# Run with visible browser
automate_rta_violations(headless=False)

print("\n" + "=" * 60)
print("NORMAL MODE TEST COMPLETED")
print("=" * 60)
