import sys
import importlib

required_modules = [
    "fastapi",
    "uvicorn",
    "pydantic",
    "pydantic_settings",
    "pytest",
    "pytest_asyncio",
    "httpx",
]

print(f"Python executable: {sys.executable}")
print(f"Python version: {sys.version}")

# Check Python version
if sys.version_info < (3, 10):
    print(f"❌ Python 3.10+ required, got {sys.version_info.major}.{sys.version_info.minor}")
    sys.exit(1)
else:
    print(f"✅ Python version {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro} OK")

print("\nChecking required modules...")
missing = []
for module in required_modules:
    try:
        mod = importlib.import_module(module)
        version = getattr(mod, "__version__", "unknown")
        print(f"✅ {module} found (version: {version})")
    except ImportError:
        print(f"❌ {module} MISSING")
        missing.append(module)

if missing:
    print(f"\n❌ Missing modules: {', '.join(missing)}")
    print("Install with: pip install -e \".[dev]\"")
    sys.exit(1)
else:
    print("\n✅ All core dependencies found.")
    sys.exit(0)
