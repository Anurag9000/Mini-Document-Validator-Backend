import sys
import importlib

required_modules = [
    "fastapi",
    "uvicorn",
    "pydantic",
    "pydantic_settings",
    "dotenv",
    "pytest",
    "httpx",
]

print(f"Python executable: {sys.executable}")
print(f"Python version: {sys.version}")

missing = []
for module in required_modules:
    try:
        importlib.import_module(module)
        print(f"✅ {module} found")
    except ImportError:
        print(f"❌ {module} MISSING")
        missing.append(module)

if missing:
    print(f"\nMissing modules: {', '.join(missing)}")
    sys.exit(1)
else:
    print("\nAll core dependencies found.")
    sys.exit(0)
