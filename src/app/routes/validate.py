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
    validate_date_range,
    validate_policy_duration,
    validate_insured_value,
    validate_insured_value_range,
    validate_policy_number,
    validate_vessel_name,
)

logger = logging.getLogger(__name__)

router = APIRouter(tags=["validation"])


@router.post("/validate", response_model=ValidationResponse)
async def validate_document(
    payload: ValidationRequest,
    extractor: AIExtractor = Depends(get_default_extractor),
    vessels: VesselRegistry = Depends(get_vessel_registry),
) -> ValidationResponse:
    """Extract fields from a document and validate them."""

    logger.info("Received validation request (text length: %d)", len(payload.text))
    
    try:
        extraction_failed = False
        try:
            extracted: ExtractedFields = extractor.extract(payload.text)
        except Exception as e:
            # Catch any unexpected extraction errors
            logger.exception("AI extraction failed with unexpected error: %s", str(e))
            extracted = ExtractedFields()
            extraction_failed = True

        # Check if vessel registry is empty and log warning
        if vessels.is_empty:
            logger.warning("Vessel registry is empty - all vessel validations will fail")
        
        checks = ValidationChecks(
            date_order_ok=validate_date_order(
                extracted.policy_start_date, extracted.policy_end_date
            ),
            insured_value_ok=validate_insured_value(extracted.insured_value),
            vessel_allowed=vessels.is_allowed(extracted.vessel_name),
            policy_number_ok=validate_policy_number(extracted.policy_number),
        )

        errors: list[str] = []
        
        # Add extraction failure warning if applicable
        if extraction_failed:
            errors.append("Field extraction encountered errors - results may be incomplete")
        
        # Missing field errors
        if not validate_policy_number(extracted.policy_number):
            errors.append("policy_number is missing or empty")
        
        if not validate_vessel_name(extracted.vessel_name):
            errors.append("vessel_name is missing or empty")
        elif not checks.vessel_allowed:
            errors.append(f"vessel_name '{extracted.vessel_name}' is not in the allowed list")

        if extracted.policy_start_date is None:
            errors.append("policy_start_date is missing or invalid format (YYYY-MM-DD)")
        elif not validate_date_range(extracted.policy_start_date):
            errors.append(
                f"policy_start_date ({extracted.policy_start_date}) is outside reasonable range (1900-2100)"
            )
        
        if extracted.policy_end_date is None:
            errors.append("policy_end_date is missing or invalid format (YYYY-MM-DD)")
        elif not validate_date_range(extracted.policy_end_date):
            errors.append(
                f"policy_end_date ({extracted.policy_end_date}) is outside reasonable range (1900-2100)"
            )

        # Logical validation errors
        if (
            extracted.policy_start_date is not None
            and extracted.policy_end_date is not None
        ):
            if not checks.date_order_ok:
                errors.append(
                    f"policy_end_date ({extracted.policy_end_date}) must be on or after "
                    f"policy_start_date ({extracted.policy_start_date})"
                )
            elif not validate_policy_duration(extracted.policy_start_date, extracted.policy_end_date):
                duration_days = (extracted.policy_end_date - extracted.policy_start_date).days
                errors.append(
                    f"policy duration ({duration_days} days) exceeds maximum allowed (50 years)"
                )

        if extracted.insured_value is not None:
            if not checks.insured_value_ok:
                errors.append(f"insured_value ({extracted.insured_value}) must be greater than zero")
            elif not validate_insured_value_range(extracted.insured_value):
                errors.append(
                    f"insured_value ({extracted.insured_value}) is outside reasonable range ($1 to $1 quadrillion)"
                )
        else:
            errors.append("insured_value is missing or invalid")

        # Determine overall validity based on all checks passing
        is_valid = (
            checks.date_order_ok
            and checks.insured_value_ok
            and checks.vessel_allowed
            and checks.policy_number_ok
            and not extraction_failed
            and (validate_date_range(extracted.policy_start_date) if extracted.policy_start_date else False)
            and (validate_date_range(extracted.policy_end_date) if extracted.policy_end_date else False)
            and (validate_policy_duration(extracted.policy_start_date, extracted.policy_end_date) if (extracted.policy_start_date and extracted.policy_end_date) else False)
            and (validate_insured_value_range(extracted.insured_value) if extracted.insured_value else False)
        )
        
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
    
    except Exception as e:
        # Catch any unexpected errors in validation logic
        logger.exception("Validation endpoint encountered unexpected error: %s", str(e))
        # Return a safe error response instead of crashing
        return ValidationResponse(
            extracted=ExtractedFields(),
            validations=ValidationChecks(
                date_order_ok=False,
                insured_value_ok=False,
                vessel_allowed=False,
                policy_number_ok=False,
            ),
            is_valid=False,
            errors=[f"Internal validation error: {str(e)}"],
        )



__all__ = ["router"]
