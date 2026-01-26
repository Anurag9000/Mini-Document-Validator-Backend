"""Validation endpoint implementation."""

from __future__ import annotations

from fastapi import APIRouter, Depends

import logging

from ..ai_extractor import AIExtractor, get_default_extractor
from ..models import (
    ExtractedFields,
    ValidationChecks,
    ValidationRequest,
    ValidationResponse,
)
from ..services.vessels import VesselRegistry, get_vessel_registry
from ..validation import (
    validate_date_order,
    validate_insured_value,
    validate_policy_number,
    validate_vessel_name,
)

logger = logging.getLogger(__name__)

router = APIRouter(tags=["validation"])


def get_extractor_dependency() -> AIExtractor:
    return get_default_extractor()


def get_vessel_registry_dependency() -> VesselRegistry:
    return get_vessel_registry()


@router.post("/validate", response_model=ValidationResponse)
async def validate_document(
    payload: ValidationRequest,
    extractor: AIExtractor = Depends(get_extractor_dependency),
    vessels: VesselRegistry = Depends(get_vessel_registry_dependency),
) -> ValidationResponse:
    """Extract fields from a document and validate them."""

    logger.info("Received validation request (text length: %d)", len(payload.text))
    
    try:
        extracted: ExtractedFields = extractor.extract(payload.text)
    except Exception as e:
        logger.exception("AI extraction failed: %s", e)
        # Fallback to empty fields or handle appropriately
        extracted = ExtractedFields()

    checks = ValidationChecks(
        date_order_ok=validate_date_order(
            extracted.policy_start_date, extracted.policy_end_date
        ),
        insured_value_ok=validate_insured_value(extracted.insured_value),
        vessel_allowed=vessels.is_allowed(extracted.vessel_name),
        policy_number_ok=validate_policy_number(extracted.policy_number),
    )

    errors: list[str] = []
    
    # Missing field errors
    if not validate_policy_number(extracted.policy_number):
        errors.append("policy_number is missing or empty")
    
    if not validate_vessel_name(extracted.vessel_name):
        errors.append("vessel_name is missing or empty")
    elif not checks.vessel_allowed:
        errors.append(f"vessel_name '{extracted.vessel_name}' is not in the allowed list")

    if extracted.policy_start_date is None:
        errors.append("policy_start_date is missing or invalid format (YYYY-MM-DD)")
    
    if extracted.policy_end_date is None:
        errors.append("policy_end_date is missing or invalid format (YYYY-MM-DD)")

    # Logical validation errors
    if (
        extracted.policy_start_date is not None
        and extracted.policy_end_date is not None
        and not checks.date_order_ok
    ):
        errors.append(
            f"policy_end_date ({extracted.policy_end_date}) must be on or after "
            f"policy_start_date ({extracted.policy_start_date})"
        )

    if extracted.insured_value is not None and not checks.insured_value_ok:
        errors.append(f"insured_value ({extracted.insured_value}) must be greater than zero")
    elif extracted.insured_value is None:
        errors.append("insured_value is missing or invalid")

    is_valid = all(checks.model_dump().values())
    
    if is_valid:
        logger.info("Validation successful for policy %s", extracted.policy_number)
    else:
        logger.warning("Validation failed with %d errors", len(errors))

    return ValidationResponse(
        extracted=extracted,
        validations=checks,
        is_valid=is_valid,
        errors=errors,
    )


__all__ = ["router", "get_extractor_dependency", "get_vessel_registry_dependency"]
