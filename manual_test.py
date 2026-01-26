import sys
sys.path.insert(0, 'src')

import asyncio
from httpx import AsyncClient
from app.main import app

async def test_health():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/health")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")

if __name__ == "__main__":
    asyncio.run(test_health())
