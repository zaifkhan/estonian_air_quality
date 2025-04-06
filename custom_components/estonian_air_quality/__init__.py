"""Estonian Ambient Air Quality integration."""
import logging
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import DOMAIN
from .coordinator import EstonianAirQualityCoordinator

_LOGGER = logging.getLogger(__name__)

PLATFORMS = ["sensor"]

async def async_setup(hass: HomeAssistant, config: dict):
    """Set up the Estonian Ambient Air Quality component."""
    hass.data.setdefault(DOMAIN, {})
    
    # Set up services
    from .services import async_setup_services
    await async_setup_services(hass)
    
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Estonian Air Quality from a config entry."""
    coordinator = EstonianAirQualityCoordinator(hass, entry)
    
    # Try to get initial data, but don't fail if it doesn't work
    try:
        await coordinator.async_config_entry_first_refresh()
    except Exception as err:
        _LOGGER.warning(f"Initial data refresh failed, continuing anyway: {err}")
        # Don't raise ConfigEntryNotReady to allow setting up even if initial refresh fails
    
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator
    
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
        
        # Check if this is the last integration instance
        if not hass.data[DOMAIN]:
            # Remove the services if no instances are left
            from .services import async_unload_services
            await async_unload_services(hass)
    
    return unload_ok
