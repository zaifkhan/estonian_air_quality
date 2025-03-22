"""Data coordinator for the Estonian Ambient Air Quality integration."""
import datetime
import logging
from typing import Any, Dict, List, Optional

import aiohttp

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    BASE_URL, 
    CONF_DATA_TYPES,
    CONF_STATIONS,
    DOMAIN,
    INDICATORS,
    STATIONS,
    UPDATE_INTERVAL,
    DATA_TYPE_POLLEN,  # Import pollen data type specifically
)

_LOGGER = logging.getLogger(__name__)

# Number of days to look back for historical data
MAX_HISTORICAL_DAYS = 7

class EstonianAirQualityCoordinator(DataUpdateCoordinator):
    """Coordinator to handle Estonian Air Quality data updates."""

    def __init__(self, hass: HomeAssistant, config_entry: ConfigEntry):
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=UPDATE_INTERVAL,
        )
        
        self.config_entry = config_entry
        self.data_types = config_entry.data[CONF_DATA_TYPES]
        self.stations = config_entry.data[CONF_STATIONS]
        self.indicators = INDICATORS  # Use hardcoded indicators
        
        # Track last successful data fetch dates
        self.last_successful_dates = {}
        self.last_checked_dates = {}
        
    async def _async_update_data(self):
        """Update data from API."""
        try:
            # Get current date for the API request
            today = datetime.datetime.now().strftime("%d.%m.%Y")
            
            # Fetch data for each selected data type and station
            data = {}
            
            for data_type in self.data_types:
                station_id = self.stations[data_type]
                
                # Use hardcoded indicators for this station
                indicators = self.get_station_indicators(data_type, station_id)
                
                if indicators:
                    indicator_str = ",".join(map(str, indicators))
                    
                    # For pollen data, implement historical lookup if needed
                    if data_type == DATA_TYPE_POLLEN:
                        data[data_type] = await self._fetch_with_historical_fallback(
                            data_type, station_id, indicator_str, today
                        )
                    else:
                        # For other data types, just use current date
                        data[data_type] = await self._fetch_data_for_date(
                            data_type, station_id, indicator_str, today, today
                        )
                    
                    # Update last checked date for this data type
                    self.last_checked_dates[data_type] = today
            
            return data
            
        except aiohttp.ClientError as error:
            raise UpdateFailed(f"Error communicating with API: {error}") from error
        except Exception as error:
            raise UpdateFailed(f"Unexpected error: {error}") from error
    
    async def _fetch_with_historical_fallback(self, data_type, station_id, indicator_str, today):
        """Fetch data with fallback to historical data if current data is not available."""
        # First try current date
        result = await self._fetch_data_for_date(data_type, station_id, indicator_str, today, today)
        
        # Check if we got any valid data
        if result and any(values for values in result.values() if values):
            # We found data for today
            self.last_successful_dates[data_type] = today
            return result
        
        # If no data for today, try previous days one by one
        current_date = datetime.datetime.now()
        
        for days_back in range(1, MAX_HISTORICAL_DAYS + 1):
            date = current_date - datetime.timedelta(days=days_back)
            date_str = date.strftime("%d.%m.%Y")
            
            # Try this historical date
            result = await self._fetch_data_for_date(data_type, station_id, indicator_str, date_str, date_str)
            
            # Check if we got any valid data
            if result and any(values for values in result.values() if values):
                # We found data for this historical date
                self.last_successful_dates[data_type] = date_str
                return result
        
        # If we reach here, we couldn't find any data
        # Return empty results or last known data
        if data_type in self.last_successful_dates:
            # Try to use the last known successful date
            last_date = self.last_successful_dates[data_type]
            return await self._fetch_data_for_date(data_type, station_id, indicator_str, last_date, last_date)
            
        # No historical data found
        return {}
    
    async def _fetch_data_for_date(self, data_type, station_id, indicator_str, start_date, end_date):
        """Fetch data for a specific date range."""
        url = f"{BASE_URL}?stations={station_id}&indicators={indicator_str}&range={start_date},{end_date}"
        
        session = async_get_clientsession(self.hass)
        try:
            async with session.get(url) as resp:
                if resp.status == 200:
                    resp_data = await resp.json()
                    
                    # Process the response data
                    result = {}
                    
                    for item in resp_data:
                        indicator_id = item["indicator"]
                        if indicator_id not in result:
                            result[indicator_id] = []
                        
                        result[indicator_id].append({
                            "measured": item["measured"],
                            "value": item["value"],
                            "station": item["station"],
                            "last_checked": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            "fetch_date": start_date,
                        })
                    
                    return result
        except Exception as ex:
            _LOGGER.error("Error fetching data for date %s: %s", start_date, ex)
        
        return {}
    
    def get_station_indicators(self, data_type, station_id):
        """Get indicators for a station from hardcoded data."""
        station_id = int(station_id)
        
        if data_type in STATIONS and station_id in STATIONS[data_type]:
            return STATIONS[data_type][station_id]["indicators"]
        
        return []