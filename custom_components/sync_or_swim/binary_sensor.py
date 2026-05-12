from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any, cast

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import STATUS_ERROR, STATUS_WARNING
from .entry_types import SyncOrSwimConfigEntry, require_runtime_coordinator
from .problem_attributes import (
    DOSING_PROBLEM_ERROR,
    DOSING_PROBLEM_OK,
    DOSING_PROBLEM_WARNING,
    dosing_problem_attributes,
)

if TYPE_CHECKING:
    from .coordinator import SyncOrSwimCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: SyncOrSwimConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator = require_runtime_coordinator(entry)
    async_add_entities([SyncOrSwimDosingProblemBinarySensor(coordinator, entry)])


class SyncOrSwimDosingProblemBinarySensor(CoordinatorEntity, BinarySensorEntity):
    _attr_device_class = BinarySensorDeviceClass.PROBLEM
    _attr_name = "SyncOrSwim Dosing Problem Active"

    def __init__(
        self, coordinator: SyncOrSwimCoordinator, entry: SyncOrSwimConfigEntry
    ) -> None:
        super().__init__(coordinator)
        self._coordinator = coordinator
        self._attr_unique_id = f"{entry.entry_id}_problem_binary"

    @property
    def is_on(self) -> bool | None:
        data = self._coordinator.data
        if not data:
            return None

        dosing_problem = data.get("dosing_problem")
        if dosing_problem:
            state = dosing_problem.get("state")
            if state in (DOSING_PROBLEM_WARNING, DOSING_PROBLEM_ERROR):
                return True
            if data.get("stale", False):
                return True
            if state == DOSING_PROBLEM_OK:
                return False
            return None

        pool = data.get("pool")
        if not pool:
            return cast(bool | None, data.get("stale", False))

        chlorine_status = pool.get("chlorine", {}).get("status")
        ph_status = pool.get("ph", {}).get("status")

        if chlorine_status in (None, "unknown") or ph_status in (None, "unknown"):
            return None

        return (
            chlorine_status in (STATUS_WARNING, STATUS_ERROR)
            or ph_status in (STATUS_WARNING, STATUS_ERROR)
            or data.get("stale", False)
        )

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        data = self._coordinator.data
        if not data:
            return {}

        return dosing_problem_attributes(data)
