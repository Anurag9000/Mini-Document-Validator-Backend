"""Validation endpoint implementation."""

from __future__ import annotations

from fastapi import APIRouter, Depends

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

    extracted: ExtractedFields = extractor.extract(payload.text)

    checks = ValidationChecks(
        date_order_ok=validate_date_order(
            extracted.policy_start_date, extracted.policy_end_date
        ),
        insured_value_ok=validate_insured_value(extracted.insured_value),
        vessel_allowed=validate_vessel_name(extracted.vessel_name, vessels.all()),
        policy_number_ok=validate_policy_number(extracted.policy_number),
    )

    errors: list[str] = []
    if extracted.policy_start_date is None:
        errors.append("policy_start_date is missing or invalid")
    if extracted.policy_end_date is None:
        errors.append("policy_end_date is missing or invalid")

    if (
        extracted.policy_start_date is not None
        and extracted.policy_end_date is not None
        and not checks.date_order_ok
    ):
        errors.append("policy_end_date must be after policy_start_date")

    if not checks.insured_value_ok:
        errors.append("insured_value must be greater than zero")
    if not checks.vessel_allowed:
        errors.append("vessel_name is not in the list of allowed vessels")
    if not checks.policy_number_ok:
        errors.append("policy_number must be provided")

    is_valid = all(checks.model_dump().values())

    return ValidationResponse(
        extracted=extracted,
        validations=checks,
        is_valid=is_valid,
        errors=errors,
    )


__all__ = ["router", "get_extractor_dependency", "get_vessel_registry_dependency"]
