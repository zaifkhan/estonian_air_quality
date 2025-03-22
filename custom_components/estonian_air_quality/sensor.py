"""Sensor platform for Estonian Ambient Air Quality integration."""
import logging
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
)

from .const import (
    DOMAIN,
    DATA_TYPE_AIR_QUALITY,
    DATA_TYPE_POLLEN,
    DATA_TYPE_RADIATION,
    DATA_TYPES,
    INDICATORS,
    STATIONS,
)

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up sensors based on a config entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    
    # Wait for first refresh to ensure we have coordinator data initialized
    await coordinator.async_config_entry_first_refresh()
    
    entities = []
    
    # Create sensors for each data type and indicator
    for data_type in coordinator.data_types:
        station_id = coordinator.stations[data_type]
        
        # Use hardcoded indicators for this station
        if data_type in STATIONS and int(station_id) in STATIONS[data_type]:
            station_data = STATIONS[data_type][int(station_id)]
            station_indicators = station_data["indicators"]
            
            for indicator_id in station_indicators:
                if data_type in INDICATORS and indicator_id in INDICATORS[data_type]:
                    indicator = INDICATORS[data_type][indicator_id]
                    
                    # Create sensor entity
                    entities.append(
                        EstonianAirQualitySensor(
                            coordinator,
                            data_type,
                            station_id,
                            indicator_id,
                            indicator,
                            station_data["name"],
                        )
                    )
    
    async_add_entities(entities)


class EstonianAirQualitySensor(CoordinatorEntity, SensorEntity):
    """Representation of an Estonian Air Quality sensor."""

    def __init__(
        self,
        coordinator: DataUpdateCoordinator,
        data_type: str,
        station_id: str,
        indicator_id: int,
        indicator: Dict[str, Any],
        station_name: str,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        
        # Entity properties
        self._data_type = data_type
        self._station_id = station_id
        self._indicator_id = indicator_id
        self._indicator = indicator
        self._station_name = station_name
        self._device_class = None  # Initialize device_class
        self._original_unit = indicator.get("unit", "")
        
        # Generate entity ID
        self._attr_unique_id = f"{data_type}_{indicator_id}_{station_id}"
        
        # Entity display details
        data_type_name = DATA_TYPES[data_type]
        indicator_name = indicator["name"]
        
        self._attr_name = f"{data_type_name} {indicator_name} {self._station_name}"
        
        # Safely check formula value
        formula = indicator.get("formula", "")
        if formula is None:  # Handle None case explicitly
            formula = ""
            
        # Determine device class and set appropriate unit
        if indicator_name == "PM10" or indicator_name == "PM2.5" or "PM" in formula:
            if "2.5" in indicator_name or "2.5" in formula:
                self._device_class = SensorDeviceClass.PM25
            else:
                self._device_class = SensorDeviceClass.PM10
            
            # Make sure to use the correct micro sign (µ instead of μ)
            self._attr_native_unit_of_measurement = "µg/m³"
        elif "CO2" in formula:
            self._device_class = SensorDeviceClass.CO2
            # Convert to ppm if needed
            self._attr_native_unit_of_measurement = "ppm" if self._original_unit == "ppm" else "ppm"
        elif "CO" in formula and "2" not in formula:
            self._device_class = SensorDeviceClass.CO
            # CO should be in ppm
            self._attr_native_unit_of_measurement = "ppm"
            # For CO, we need to convert mg/m³ to ppm during value calculation
        else:
            # For sensors without special device class, use the original unit
            self._attr_native_unit_of_measurement = self._original_unit
            
        self._attr_state_class = SensorStateClass.MEASUREMENT
        
        # Set suggested display precision
        if self._attr_native_unit_of_measurement == "µg/m³":
            self._attr_suggested_display_precision = 1
    
    @property
    def device_class(self):
        """Return the device class."""
        return self._device_class
    
    @property
    def native_value(self) -> Optional[float]:
        """Return the state of the sensor."""
        if (
            self.coordinator.data
            and self._data_type in self.coordinator.data
            and self._indicator_id in self.coordinator.data[self._data_type]
        ):
            data_points = self.coordinator.data[self._data_type][self._indicator_id]
            if data_points:
                # Get the latest measurement
                latest = max(data_points, key=lambda x: datetime.fromisoformat(x["measured"].replace(" ", "T")))
                try:
                    value = float(latest["value"])
                    
                    # Convert CO from mg/m³ to ppm if needed
                    if (self._device_class == SensorDeviceClass.CO and 
                        self._original_unit == "mg/m³" and
                        self._attr_native_unit_of_measurement == "ppm"):
                        # Conversion factor for CO: 1 mg/m³ ≈ 0.873 ppm at 25°C and 1 atm
                        value = value * 0.873
                        
                    return value
                except (ValueError, TypeError):
                    return None
        
        return None
    
    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        """Return the state attributes."""
        attrs = {
            "station_id": self._station_id,
            "station_name": self._station_name,
            "indicator_id": self._indicator_id,
            "indicator_name": self._indicator["name"],
            "description": self._indicator.get("description", ""),
            "formula": self._indicator.get("formula", ""),
            "data_type": self._data_type,
            "original_unit": self._original_unit,
        }
        
        # Add measurement timestamps and data source information
        if (
            self.coordinator.data
            and self._data_type in self.coordinator.data
            and self._indicator_id in self.coordinator.data[self._data_type]
        ):
            data_points = self.coordinator.data[self._data_type][self._indicator_id]
            if data_points:
                latest = max(data_points, key=lambda x: datetime.fromisoformat(x["measured"].replace(" ", "T")))
                
                # Add timestamp of the measurement
                attrs["last_measured"] = latest["measured"]
                
                # Add information about when the data was checked/fetched
                if "last_checked" in latest:
                    attrs["last_checked"] = latest["last_checked"]
                
                # Add the date that was used to fetch the data (could be historical)
                if "fetch_date" in latest:
                    attrs["fetch_date"] = latest["fetch_date"]
                    
                    # If the fetch date is not today's date, indicate this is historical data
                    today = datetime.now().strftime("%d.%m.%Y")
                    if latest["fetch_date"] != today:
                        attrs["is_historical"] = True
        
        # Add last successful date from coordinator if available
        if hasattr(self.coordinator, "last_successful_dates") and self._data_type in self.coordinator.last_successful_dates:
            attrs["last_successful_date"] = self.coordinator.last_successful_dates[self._data_type]
        
        # Add last checked date from coordinator if available
        if hasattr(self.coordinator, "last_checked_dates") and self._data_type in self.coordinator.last_checked_dates:
            attrs["coordinator_last_checked"] = self.coordinator.last_checked_dates[self._data_type]
        
        return attrs