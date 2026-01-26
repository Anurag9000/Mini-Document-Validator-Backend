import sys
import traceback

sys.path.insert(0, 'src')

try:
    from app.models import ExtractedFields
    print("Import successful!")
except Exception as e:
    print(f"Error: {e}")
    print("\nFull traceback:")
    traceback.print_exc()
