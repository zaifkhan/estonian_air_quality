"""Config flow for Estonian Ambient Air Quality integration."""
import logging
from typing import Any, Dict, List, Optional

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant, callback
from homeassistant.data_entry_flow import FlowResult
import homeassistant.helpers.config_validation as cv

from .const import (
    CONF_DATA_TYPES,
    CONF_STATIONS,
    DATA_TYPES,
    DOMAIN,
    STATIONS,
)

_LOGGER = logging.getLogger(__name__)

class EstonianAirQualityConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Estonian Ambient Air Quality."""

    VERSION = 1
    
    def __init__(self):
        """Initialize the config flow."""
        self.data = {}
        
    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}
        
        if user_input is not None:
            self.data[CONF_DATA_TYPES] = user_input[CONF_DATA_TYPES]
            self.data[CONF_STATIONS] = {}
            
            return await self.async_step_select_stations()
        
        data_types_schema = vol.Schema({
            vol.Required(CONF_DATA_TYPES): cv.multi_select(DATA_TYPES)
        })
        
        return self.async_show_form(
            step_id="user",
            data_schema=data_types_schema,
            errors=errors,
        )
    
    async def async_step_select_stations(self, user_input=None):
        """Let the user select stations for each data type."""
        errors = {}
        
        # Check which data type to show
        current_data_type = next(
            (dt for dt in self.data[CONF_DATA_TYPES] if dt not in self.data[CONF_STATIONS]),
            None,
        )
        
        if not current_data_type:
            # All stations selected, finish the flow
            return self.async_create_entry(
                title="Estonian Ambient Air Quality",
                data=self.data,
            )
        
        if user_input is not None:
            # Save the selected station for the current data type
            station_id = user_input["station"]
            self.data[CONF_STATIONS][current_data_type] = station_id
            
            # Move to the next data type or finish if all done
            return await self.async_step_select_stations()
        
        # Create schema for station selection using hardcoded stations
        station_options = {}
        if current_data_type in STATIONS:
            for station_id, station_data in STATIONS[current_data_type].items():
                station_options[str(station_id)] = station_data["name"]
        
        return self.async_show_form(
            step_id="select_stations",
            data_schema=vol.Schema({
                vol.Required("station"): vol.In(station_options)
            }),
            errors=errors,
            description_placeholders={"data_type": DATA_TYPES[current_data_type]},
        )