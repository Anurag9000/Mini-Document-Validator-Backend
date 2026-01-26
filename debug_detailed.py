#!/usr/bin/env python
"""Debug script to find the exact Pydantic error."""
import sys
sys.path.insert(0, 'src')

if __name__ == "__main__":
    try:
        print("Attempting to import app.models...")
        from app import models
        print("✓ Successfully imported app.models")
        
        print("\nAttempting to create ExtractedFields...")
        from app.models import ExtractedFields
        print("✓ Successfully imported ExtractedFields")
        
        print("\nAttempting to instantiate ExtractedFields...")
        fields = ExtractedFields()
        print(f"✓ Successfully created: {fields}")
        
        print("\n✅ ALL IMPORTS SUCCESSFUL!")
        
    except Exception as e:
        print(f"\n❌ ERROR: {type(e).__name__}")
        print(f"Message: {e}")
        print("\nFull traceback:")
        import traceback
        traceback.print_exc()
        sys.exit(1)
