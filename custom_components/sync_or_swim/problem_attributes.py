from __future__ import annotations

from typing import Any

DOSING_PROBLEM_OK = "OK"
DOSING_PROBLEM_ERROR = "Error"
DOSING_PROBLEM_WARNING = "Warning"
STALE_PROBLEM_MESSAGE = "Latest reading is stale"
STALE_PROBLEM_REASON = "stale_data"


def dosing_problem_attributes(data: dict[str, Any]) -> dict[str, Any]:
    """Build shared attributes for dosing problem entities."""
    pool = data.get("pool")
    dosing_problem = data.get("dosing_problem")
    problem_state = dosing_problem.get("state") if dosing_problem else None
    problem_reason = dosing_problem.get("reason") if dosing_problem else None
    problem_message = dosing_problem.get("message") if dosing_problem else None
    if data.get("stale", False) and problem_state != DOSING_PROBLEM_ERROR:
        problem_reason = STALE_PROBLEM_REASON
        problem_message = STALE_PROBLEM_MESSAGE

    attributes = {
        "stale": data.get("stale", False),
        "stale_since": data.get("captured_at") if data.get("stale") else None,
        "error": data.get("error"),
        "problem_reason": problem_reason,
        "problem_message": problem_message,
    }

    if dosing_problem:
        chlorine_status = dosing_problem.get("chlorine_status")
        ph_status = dosing_problem.get("ph_status")
        attributes.update(
            {
                "chlorine_status": chlorine_status
                or (pool["chlorine"]["status"] if pool else None),
                "ph_status": ph_status or (pool["ph"]["status"] if pool else None),
            }
        )
    elif pool:
        attributes.update(
            {
                "chlorine_status": pool["chlorine"]["status"],
                "ph_status": pool["ph"]["status"],
            }
        )

    return attributes
