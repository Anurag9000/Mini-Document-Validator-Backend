import sys
sys.path.insert(0, 'src')
import traceback

try:
    from app.models import ExtractedFields
    print("SUCCESS - Import worked!")
except Exception as e:
    print(f"ERROR: {type(e).__name__}: {e}")
    traceback.print_exc()
