"""Services for Estonian Ambient Air Quality integration."""
import logging
import voluptuous as vol

from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers import config_validation as cv, entity_registry as er

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

SERVICE_UPDATE_AIR_QUALITY_DATA = "update_air_quality_data"

SERVICE_UPDATE_AIR_QUALITY_DATA_SCHEMA = vol.Schema({
    vol.Required("entity_id"): cv.entity_id,
})

async def async_setup_services(hass: HomeAssistant) -> None:
    """Set up services for Estonian Ambient Air Quality integration."""
    
    async def async_update_air_quality_data(call: ServiceCall) -> None:
        """Force update of air quality data."""
        entity_id = call.data["entity_id"]
        
        # Get the entity registry entry to find the config entry ID
        registry = er.async_get(hass)
        entity_entry = registry.async_get(entity_id)
        
        if not entity_entry or entity_entry.platform != DOMAIN:
            _LOGGER.error(
                "Service %s called with invalid entity_id: %s",
                SERVICE_UPDATE_AIR_QUALITY_DATA,
                entity_id,
            )
            return
        
        # Get coordinator for this entity
        config_entry_id = entity_entry.config_entry_id
        coordinator = hass.data[DOMAIN].get(config_entry_id)
        
        if not coordinator:
            _LOGGER.error(
                "Coordinator not found for entity %s (config entry %s)",
                entity_id,
                config_entry_id,
            )
            return
        
        # Force update
        await coordinator.force_update()
        _LOGGER.debug("Forced update for entity %s", entity_id)
    
    # Register the service
    hass.services.async_register(
        DOMAIN,
        SERVICE_UPDATE_AIR_QUALITY_DATA,
        async_update_air_quality_data,
        schema=SERVICE_UPDATE_AIR_QUALITY_DATA_SCHEMA,
    )

async def async_unload_services(hass: HomeAssistant) -> None:
    """Unload Estonian Ambient Air Quality services."""
    if hass.services.has_service(DOMAIN, SERVICE_UPDATE_AIR_QUALITY_DATA):
        hass.services.async_remove(DOMAIN, SERVICE_UPDATE_AIR_QUALITY_DATA)
