import sys
import os
import asyncio
from httpx import AsyncClient
from app.main import app

# Path setup
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(current_dir)
sys.path.insert(0, os.path.join(root_dir, "src"))

async def main():
    print("Running Final Verification...\n")
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        
        # Test 1: Invalid Date (Crash Prevention)
        print("Test 1: Invalid Date (2024-02-31)")
        # Regex matches, but date is invalid. Should NOT crash.
        payload = {
            "text": "Policy Number: POL-1\nVessel Name: Sea Breeze\nPolicy Start Date: 2024-02-31\nPolicy End Date: 2024-06-30\nInsured Value: 1000"
        }
        resp = await client.post("/validate", json=payload)
        data = resp.json()
        if resp.status_code == 200:
            print("  ✅ Status 200 (No Crash)")
            # Should have an error about start date being missing/invalid
            if "policy_start_date is missing or invalid" in data["errors"]:
                print("  ✅ Correct Error Message Found")
            else:
                print(f"  ⚠️ Unexpected Error Messages: {data['errors']}")
        else:
            print(f"  ❌ Failed with Status {resp.status_code}")

        print("-" * 20)

        # Test 2: Currency Symbol
        print("Test 2: Currency Parsing ($1,000.00)")
        payload = {
            "text": "Policy Number: POL-1\nVessel Name: Sea Breeze\nPolicy Start Date: 2024-01-01\nPolicy End Date: 2024-06-30\nInsured Value: $1,000.00"
        }
        resp = await client.post("/validate", json=payload)
        data = resp.json()
        if data["extracted"]["insured_value"] == 1000.0:
             print("  ✅ Insured Value Parsed Correctly (1000.0)")
        else:
             print(f"  ❌ Failed Parsing: {data['extracted']['insured_value']}")

        print("-" * 20)
        
        # Test 3: Missing Date Logic
        print("Test 3: Missing End Date")
        payload = {
            "text": "Policy Number: POL-1\nVessel Name: Sea Breeze\nPolicy Start Date: 2024-01-01\nInsured Value: 1000"
        }
        resp = await client.post("/validate", json=payload)
        data = resp.json()
        if "policy_end_date is missing or invalid" in data["errors"]:
            print("  ✅ Correct Error Message Found")
        if "policy_end_date must be after policy_start_date" not in data["errors"]:
             print("  ✅ Confusing Order Error Message SUPPRESSED")
        else:
             print("  ❌ Confusing Order Error Message PRESENT")

        print("-" * 20)

if __name__ == "__main__":
    asyncio.run(main())
