import sys
import os
import asyncio
from httpx import AsyncClient

# Path setup
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(current_dir)
sys.path.insert(0, os.path.join(root_dir, "src"))

from app.main import app
from app.services.vessels import get_vessel_registry

def verify_registry_load():
    try:
        registry = get_vessel_registry()
        print(f"Count: {len(registry.all())}")
        print(f"Allowed('Sea Breeze'): {registry.is_allowed('Sea Breeze')}")
    except Exception as e:
        print(f"Registry Error: {e}")

async def verify_endpoint():
    async with AsyncClient(app=app, base_url="http://test") as client:
        payload = {
            "text": "Policy Number: POL-1\nVessel Name: Sea Breeze\nPolicy Start Date: 2024-01-01\nPolicy End Date: 2024-01-01\nInsured Value: 1000"
        }
        resp = await client.post("/validate", json=payload)
        data = resp.json()
        print(f"Valid: {data.get('is_valid')}")
        if data.get('errors'):
             print(f"Errors: {data['errors']}")

if __name__ == "__main__":
    # verify_registry_load()
    asyncio.run(verify_endpoint())
