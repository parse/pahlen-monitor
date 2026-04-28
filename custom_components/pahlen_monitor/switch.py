import logging

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import CONF_ROLE, DOMAIN, ROLE_PRODUCER

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
):
    if entry.data.get(CONF_ROLE) != ROLE_PRODUCER:
        return

    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([PahlenInstallationEnabledSwitch(coordinator, entry)])


class PahlenInstallationEnabledSwitch(CoordinatorEntity, SwitchEntity):
    _attr_name = "Pahlen Installation Enabled"
    _attr_icon = "mdi:pool"

    def __init__(self, coordinator, entry):
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_installation_enabled"

    @property
    def is_on(self) -> bool:
        return self.coordinator.installation_enabled

    async def async_turn_on(self, **kwargs) -> None:
        _LOGGER.debug("Enabling Pahlen installation monitoring")
        await self.coordinator.async_set_installation_enabled(True)

    async def async_turn_off(self, **kwargs) -> None:
        _LOGGER.debug("Disabling Pahlen installation monitoring")
        await self.coordinator.async_set_installation_enabled(False)
