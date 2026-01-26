#!/usr/bin/env python
"""Find the exact Pydantic error with full details."""
import sys
import os

# Disable Pydantic's strict mode to get better error messages
os.environ['PYDANTIC_SKIP_VALIDATING_CORE_SCHEMAS'] = '0'

sys.path.insert(0, 'src')

try:
    print("Step 1: Importing pydantic...")
    import pydantic
    print(f"✓ Pydantic version: {pydantic.VERSION}")
    
    print("\nStep 2: Importing datetime and typing...")
    from datetime import date
    from typing import Optional, Union
    print("✓ Imports successful")
    
    print("\nStep 3: Importing pydantic components...")
    from pydantic import BaseModel, Field, field_validator
    print("✓ Pydantic components imported")
    
    print("\nStep 4: Importing app.models...")
    from app import models
    print("✓ app.models imported")
    
    print("\nStep 5: Importing ExtractedFields...")
    from app.models import ExtractedFields
    print("✓ ExtractedFields imported")
    
    print("\n✅ ALL SUCCESSFUL!")
    
except Exception as e:
    print(f"\n❌ FAILED at current step")
    print(f"Error type: {type(e).__name__}")
    print(f"Error message: {str(e)}")
    
    # Get more details if it's a Pydantic error
    if hasattr(e, '__cause__'):
        print(f"\nCause: {e.__cause__}")
    if hasattr(e, '__context__'):
        print(f"Context: {e.__context__}")
    
    print("\nFull traceback:")
    import traceback
    traceback.print_exc()
    sys.exit(1)
