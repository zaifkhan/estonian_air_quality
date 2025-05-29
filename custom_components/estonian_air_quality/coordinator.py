"""Data coordinator for the Estonian Ambient Air Quality integration."""
import datetime
import logging
import json
from typing import Any, Dict, List, Optional
import asyncio

import aiohttp

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, ServiceCall
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
    DATA_TYPE_TO_API_TYPE,
    DATA_TYPE_POLLEN,  # Import pollen data type specifically
)

_LOGGER = logging.getLogger(__name__)

# Number of days to look back for historical data
MAX_HISTORICAL_DAYS = 7
# Maximum retries for API requests
MAX_RETRIES = 3
# Default timeout for API requests in seconds
DEFAULT_TIMEOUT = 30
# Extended data window (days)
EXTENDED_DATA_WINDOW = 3  # 3 days instead of 1

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
        
        # Track API status for diagnostics
        self.api_status = {}
        
    async def _async_update_data(self):
        """Update data from API."""
        try:
            # Get current date for the API request
            today = datetime.datetime.now().strftime("%d.%m.%Y")
            
            # Calculate date for extended window
            extended_start_date = (datetime.datetime.now() - datetime.timedelta(days=EXTENDED_DATA_WINDOW)).strftime("%d.%m.%Y")
            
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
                            data_type, station_id, indicator_str, extended_start_date, today
                        )
                    else:
                        # For other data types, use extended date range
                        data[data_type] = await self._fetch_data_for_date_range(
                            data_type, station_id, indicator_str, extended_start_date, today
                        )
                    
                    # Update last checked date for this data type
                    self.last_checked_dates[data_type] = today
                    
                    # Update API status
                    if data_type not in self.api_status:
                        self.api_status[data_type] = {}
                    self.api_status[data_type]["last_checked"] = datetime.datetime.now().isoformat()
                    
                    # If we got data, mark success
                    if data[data_type]:
                        self.api_status[data_type]["status"] = "success"
                    else:
                        self.api_status[data_type]["status"] = "no_data"
            
            return data
            
        except aiohttp.ClientError as error:
            for data_type in self.data_types:
                if data_type not in self.api_status:
                    self.api_status[data_type] = {}
                self.api_status[data_type]["status"] = "connection_error"
                self.api_status[data_type]["error"] = str(error)
                self.api_status[data_type]["last_checked"] = datetime.datetime.now().isoformat()
            
            # If we have previous data, return it instead of raising an error
            if hasattr(self, "data") and self.data:
                _LOGGER.warning(f"Connection error, using cached data: {error}")
                return self.data
                
            raise UpdateFailed(f"Error communicating with API: {error}") from error
        except Exception as error:
            for data_type in self.data_types:
                if data_type not in self.api_status:
                    self.api_status[data_type] = {}
                self.api_status[data_type]["status"] = "error"
                self.api_status[data_type]["error"] = str(error)
                self.api_status[data_type]["last_checked"] = datetime.datetime.now().isoformat()
            
            # If we have previous data, return it instead of raising an error
            if hasattr(self, "data") and self.data:
                _LOGGER.warning(f"Unexpected error, using cached data: {error}")
                return self.data
                
            raise UpdateFailed(f"Unexpected error: {error}") from error
    
    async def _fetch_with_historical_fallback(self, data_type, station_id, indicator_str, start_date, end_date):
        """Fetch data with fallback to historical data if current data is not available."""
        # First try current date range
        result = await self._fetch_data_for_date_range(data_type, station_id, indicator_str, start_date, end_date)
        
        # Check if we got any valid data
        if result and any(values for values in result.values() if values):
            # We found data for the date range
            self.last_successful_dates[data_type] = end_date
            return result
        
        # If no data for the current range, try previous days one by one
        current_date = datetime.datetime.now()
        
        for days_back in range(EXTENDED_DATA_WINDOW + 1, MAX_HISTORICAL_DAYS + 1):
            end_date = current_date - datetime.timedelta(days=days_back - EXTENDED_DATA_WINDOW)
            start_date = current_date - datetime.timedelta(days=days_back)
            end_date_str = end_date.strftime("%d.%m.%Y")
            start_date_str = start_date.strftime("%d.%m.%Y")
            
            # Try this historical date range
            result = await self._fetch_data_for_date_range(data_type, station_id, indicator_str, start_date_str, end_date_str)
            
            # Check if we got any valid data
            if result and any(values for values in result.values() if values):
                # We found data for this historical date range
                self.last_successful_dates[data_type] = end_date_str
                return result
        
        # If we reach here, we couldn't find any data
        # Return empty results or last known data
        if data_type in self.last_successful_dates:
            # Try to use the last known successful date
            last_date = self.last_successful_dates[data_type]
            last_start_date = (datetime.datetime.strptime(last_date, "%d.%m.%Y") - 
                              datetime.timedelta(days=EXTENDED_DATA_WINDOW)).strftime("%d.%m.%Y")
            return await self._fetch_data_for_date_range(data_type, station_id, indicator_str, last_start_date, last_date)
            
        # No historical data found
        return {}
    
    async def _fetch_data_for_date_range(self, data_type, station_id, indicator_str, start_date, end_date):
        """Fetch data for a specific date range with retry logic."""
        api_type = DATA_TYPE_TO_API_TYPE.get(data_type, "INDICATOR") # Default to INDICATOR if not found
        url = f"{BASE_URL}?stations={station_id}&indicators={indicator_str}&range={start_date},{end_date}&type={api_type}"
        
        session = async_get_clientsession(self.hass)
        
        # Initialize retry counter
        retries = 0
        
        while retries < MAX_RETRIES:
            try:
                _LOGGER.debug(f"Fetching data for {data_type} from {url}, attempt {retries+1}/{MAX_RETRIES}")
                
                async with session.get(url, timeout=DEFAULT_TIMEOUT) as resp:
                    if resp.status == 200:
                        # Get response text with proper encoding
                        try:
                            # First try to get the text with the encoding from Content-Type header
                            resp_data = await resp.text()
                        except UnicodeDecodeError:
                            # If that fails, try with utf-8
                            _LOGGER.debug("Retrying with explicit UTF-8 encoding")
                            resp_data = await resp.read()
                            resp_data = resp_data.decode('utf-8', errors='replace')
                        
                        # Parse the response data
                        try:
                            resp_json = json.loads(resp_data)
                        except json.JSONDecodeError:
                            # Try again with Latin-1 encoding which is more permissive
                            _LOGGER.debug("JSON decode failed, trying with Latin-1 encoding")
                            try:
                                resp_data = await resp.read()
                                resp_data = resp_data.decode('latin-1', errors='replace')
                                resp_json = json.loads(resp_data)
                            except Exception as enc_err:
                                _LOGGER.error(f"Failed encoding attempt: {enc_err}")
                                # Increment retry counter and try again
                                retries += 1
                                if retries < MAX_RETRIES:
                                    await asyncio.sleep(2)  # Wait before retrying
                                    continue
                                return {}
                        
                        # Process the response data
                        result = {}
                        
                        for item in resp_json:
                            indicator_id = item["indicator"]
                            if indicator_id not in result:
                                result[indicator_id] = []
                            
                            result[indicator_id].append({
                                "measured": item["measured"],
                                "value": item["value"],
                                "station": item["station"],
                                "last_checked": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                "fetch_date": end_date,
                                "status": "success",
                                "returned_code": f"station_{item['station']}",
                            })
                        
                        return result
                    
                    # Handle non-200 responses
                    _LOGGER.warning(f"API returned status {resp.status} for {data_type}")
                    
                    # Update status
                    if data_type not in self.api_status:
                        self.api_status[data_type] = {}
                    self.api_status[data_type]["http_status"] = resp.status
                    
                    # Increment retry counter and try again
                    retries += 1
                    if retries < MAX_RETRIES:
                        await asyncio.sleep(2)  # Wait before retrying
                        continue
                    
                    # All retries failed
                    return {}
                
            except asyncio.TimeoutError:
                _LOGGER.warning(f"Timeout fetching data for {data_type}")
                
                # Update status
                if data_type not in self.api_status:
                    self.api_status[data_type] = {}
                self.api_status[data_type]["status"] = "timeout"
                
                # Increment retry counter and try again
                retries += 1
                if retries < MAX_RETRIES:
                    await asyncio.sleep(2)  # Wait before retrying
                    continue
                
                # All retries failed
                return {}
                
            except Exception as ex:
                _LOGGER.error(f"Error fetching data for {data_type}: {ex}")
                
                # Update status
                if data_type not in self.api_status:
                    self.api_status[data_type] = {}
                self.api_status[data_type]["status"] = "error"
                self.api_status[data_type]["error"] = str(ex)
                
                # Increment retry counter and try again
                retries += 1
                if retries < MAX_RETRIES:
                    await asyncio.sleep(2)  # Wait before retrying
                    continue
                
                # All retries failed
                return {}
        
        # All retries exhausted
        return {}
    
    def get_station_indicators(self, data_type, station_id):
        """Get indicators for a station from hardcoded data."""
        station_id = int(station_id)
        
        if data_type in STATIONS and station_id in STATIONS[data_type]:
            return STATIONS[data_type][station_id]["indicators"]
        
        return []
        
    async def force_update(self):
        """Force an immediate update of the data."""
        _LOGGER.debug("Force updating data")
        await self.async_refresh()
