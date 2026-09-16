from datetime import datetime, timezone

from fastapi import HTTPException, status

from app.models.maintenance import (
    Maintenance,
    MaintenanceStatus,
)


VALID_TRANSITIONS: dict[
    MaintenanceStatus,
    set[MaintenanceStatus],
] = {
    MaintenanceStatus.OPEN: {
        MaintenanceStatus.ASSIGNED,
    },
    MaintenanceStatus.ASSIGNED: {
        MaintenanceStatus.IN_PROGRESS,
    },
    MaintenanceStatus.IN_PROGRESS: {
        MaintenanceStatus.RESOLVED,
    },
    MaintenanceStatus.RESOLVED: set(),
}


def transition_maintenance_status(
    maintenance: Maintenance,
    new_status: MaintenanceStatus,
) -> None:
    allowed_statuses = VALID_TRANSITIONS[
        maintenance.status
    ]

    if new_status not in allowed_statuses:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                f"Invalid maintenance transition: "
                f"{maintenance.status.value} "
                f"-> {new_status.value}."
            ),
        )

    maintenance.status = new_status

    if new_status == MaintenanceStatus.RESOLVED:
        maintenance.resolved_at = datetime.now(
            timezone.utc
        )