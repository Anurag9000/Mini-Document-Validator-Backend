import sys
import os

# Path setup
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(current_dir)
sys.path.insert(0, os.path.join(root_dir, "src"))

from app.models import ExtractedFields
from pydantic import ValidationError

print("Testing Invalid Date Parsing:")
# 2024-02-31 Matches regex \d{4}-\d{2}-\d{2} but is invalid calendar date
try:
    data = {"policy_start_date": "2024-02-31"}
    model = ExtractedFields.model_validate(data)
    print("❌ Model validated '2024-02-31' as valid (Unexpected)")
except ValidationError as e:
    print(f"✅ Caught expected ValidationError: {e}")
except ValueError as e:
    print(f"❌ Caught raw ValueError (Should be wrapped!): {e}")

print("\nTesting Extractor Integration:")
from app.ai_extractor import RuleBasedAIExtractor
extractor = RuleBasedAIExtractor()
# Text with invalid date
text = "Policy Start Date: 2024-02-31"

try:
    # This calls model_validate internally
    result = extractor.extract(text)
    print(f"❌ Extracted successfully: {result}")
except ValidationError as e:
    print(f"✅ Caught ValidationError during extraction: {e}")
except Exception as e:
    print(f"❌ Crashed with generic exception: {type(e).__name__}: {e}")
