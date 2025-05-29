"""Constants for the Estonian Ambient Air Quality integration."""
from datetime import timedelta

DOMAIN = "estonian_air_quality"

# Base URL for fetching air quality data
BASE_URL = "https://ohuseire.ee/api/monitoring/en"

# Available data types
DATA_TYPE_AIR_QUALITY = "airquality"
DATA_TYPE_POLLEN = "pollen"
DATA_TYPE_RADIATION = "radiation"

DATA_TYPES = {
    DATA_TYPE_AIR_QUALITY: "Air Quality",
    DATA_TYPE_POLLEN: "Pollen",
    DATA_TYPE_RADIATION: "Radiation",
}

DATA_TYPE_TO_API_TYPE = {
    DATA_TYPE_AIR_QUALITY: "INDICATOR",
    DATA_TYPE_POLLEN: "POLLEN",
    DATA_TYPE_RADIATION: "RADIATION",
}

# URLs for station and indicator API endpoints
STATION_URL = {
    DATA_TYPE_AIR_QUALITY: "https://ohuseire.ee/api/station/en?type=INDICATOR",
    DATA_TYPE_POLLEN: "https://ohuseire.ee/api/station/en?type=POLLEN",
    DATA_TYPE_RADIATION: "https://ohuseire.ee/api/station/en?type=RADIATION",
}

INDICATOR_URL = {
    DATA_TYPE_AIR_QUALITY: "https://ohuseire.ee/api/indicator/en?type=INDICATOR",
    DATA_TYPE_POLLEN: "https://ohuseire.ee/api/indicator/en?type=POLLEN",
    DATA_TYPE_RADIATION: "https://ohuseire.ee/api/indicator/en?type=RADIATION",
}

# Config flow keys
CONF_DATA_TYPES = "data_types"
CONF_STATIONS = "stations"

# Update interval
UPDATE_INTERVAL = timedelta(hours=1)

# Sensor friendly names
FRIENDLY_NAME_TEMPLATE = "{data_type}_{indicator}_{station}"

# Hardcoded indicator and station data
# Air Quality Indicators
AIR_QUALITY_INDICATORS = {
    1: {"id": 1, "name": "Sulphur dioxide", "formula": "SO2", "unit": "μg/m³", "description": "Sulphur dioxide is emitted to ambient air from burning sulphur containing fuels."},
    3: {"id": 3, "name": "Nitrogen dioxide", "formula": "NO2", "unit": "μg/m³", "description": "Nitrogen dioxide is emitted to ambient air from combustion where air nitrogen is reacting with oxygen at elevated temperatures."},
    4: {"id": 4, "name": "Carbon monoxide", "formula": "CO", "unit": "mg/m³", "description": "Carbon monoxide is emitted from incomplete combustion of carbon based fuels."},
    6: {"id": 6, "name": "Ozone", "formula": "O3", "unit": "μg/m³", "description": "Ground level ozone is formed in atmosphere photochemical reactions."},
    8: {"id": 8, "name": "Volatile organic compounds", "formula": "NMHC", "unit": "μgC/m³", "description": "Volatile organic compounds are class of organic compounds whose partial pressure is over 0.01 kPa at 20°C."},
    10: {"id": 10, "name": "Ammonia", "formula": "NH3", "unit": "μg/m³", "description": "Ammonia is gaseous substance with strong irritating smell."},
    11: {"id": 11, "name": "Hydrogen sulphide", "formula": "H2S", "unit": "μg/m³", "description": "Hydrogen sulphide is gaseous substance with unpleasant smell."},
    13: {"id": 13, "name": "Mercury", "formula": "Hg", "unit": "ng/m³", "description": ""},
    14: {"id": 14, "name": "Benzene", "formula": "C6H6", "unit": "μg/m³", "description": "Benzene is aromatic hydrocarbon which consists of only one aromatic cycle."},
    16: {"id": 16, "name": "Toluene", "formula": "C7H8", "unit": "μg/m³", "description": ""},
    18: {"id": 18, "name": "Xylene", "formula": "C8H10", "unit": "μg/m³", "description": ""},
    20: {"id": 20, "name": "TSP", "formula": "TSP", "unit": "", "description": ""},
    21: {"id": 21, "name": "PM10", "formula": "PM10", "unit": "μg/m³", "description": "Solid and liquid particulate matter with aerodynamic diameter less than 10 micrometres."},
    23: {"id": 23, "name": "PM2.5", "formula": "PM2.5", "unit": "μg/m³", "description": "Solid and liquid particulate matter with aerodynamic diameter less than 2.5 micrometres."},
    34: {"id": 34, "name": "Temperature", "formula": "TEMP", "unit": "C", "description": "Ambient temperature is measured continuously with thermometer at 2 m."},
    37: {"id": 37, "name": "Wind direction at 10 m", "formula": "WD10", "unit": "deg", "description": "Wind direction shows this point at horizon from where wind is blowing."},
    41: {"id": 41, "name": "Wind speed at 10 m", "formula": "WS10", "unit": "m/s", "description": "Wind speed is measured at 10 m using ultrasonic anemometer."},
    66: {"id": 66, "name": "Temperature at 10 m", "formula": "TEMP10", "unit": "C", "description": "Ambient temperature is measured continuously with thermometer at 10 m."},
}

# Pollen Indicators
POLLEN_INDICATORS = {
    44: {"id": 44, "name": "Alternaria", "formula": None, "unit": "tk/m³", "description": "Alternaria is a genus of ascomycete fungi."},
    47: {"id": 47, "name": "Juniper", "formula": None, "unit": "tk/m³", "description": "Junipers are coniferous plants in the genus Juniperus of the cypress family Cupressaceae."},
    48: {"id": 48, "name": "Birch", "formula": None, "unit": "tk/m³", "description": "Birch is a thinleaved deciduous hardwood tree of the genus Betula in the family Betulaceae."},
    49: {"id": 49, "name": "Grasses", "formula": None, "unit": "tk/m³", "description": "The Poaceae (also called Gramineae or true grasses) are a large and nearly ubiquitous family of monocotyledonous flowering plants."},
    51: {"id": 51, "name": "Alder", "formula": None, "unit": "tk/m³", "description": "Alder is the common name of a genus of flowering plants (Alnus) belonging to the birch family Betulaceae."},
    57: {"id": 57, "name": "Wormwood", "formula": None, "unit": "tk/m³", "description": "Artemisia vulgaris (mugwort or common wormwood) is one of several species in the genus Artemisia commonly known as mugwort."},
    59: {"id": 59, "name": "Hazel", "formula": None, "unit": "tk/m³", "description": "The hazel (Corylus) is a genus of deciduous trees and large shrubs native to the temperate Northern Hemisphere."},
    62: {"id": 62, "name": "Saltbush", "formula": None, "unit": "tk/m³", "description": "Atriplex is a plant genus of 250-300 species, known by the common names of saltbush and orache (or orach)."},
}

# Radiation Indicators
RADIATION_INDICATORS = {
    80: {"id": 80, "name": "Radiation", "formula": None, "unit": "nSv/h", "description": "Ambient radiation measurement."},
}

# Air Quality Stations
AIR_QUALITY_STATIONS = {
    1: {"id": 1, "name": "Kohtla-Järve", "indicators": [11, 1, 3, 4, 21, 23, 6, 34, 37, 41]},
    3: {"id": 3, "name": "Lahemaa", "indicators": [1, 3, 4, 6, 13, 23, 34, 37, 41]},
    4: {"id": 4, "name": "Narva", "indicators": [1, 3, 4, 6, 11, 21, 23, 34, 37, 41]},
    5: {"id": 5, "name": "Liivalaia", "indicators": [21, 23, 3, 4, 6, 1]},
    6: {"id": 6, "name": "Rahu", "indicators": [1, 3, 4, 6, 21, 11]},
    7: {"id": 7, "name": "Õismäe", "indicators": [1, 3, 4, 6, 14, 16, 18, 21, 23]},
    8: {"id": 8, "name": "Tartu", "indicators": [21, 23, 4, 3, 1, 6, 37, 41, 66]},
    9: {"id": 9, "name": "Vilsandi", "indicators": [1, 3, 6, 23, 34, 37, 41, 81, 82]},
    10: {"id": 10, "name": "Saarejärve", "indicators": [1, 3, 6, 23, 34, 37, 41]},
    16: {"id": 16, "name": "Paldiski", "indicators": [8, 14, 16, 18, 34, 37, 41]},
    21: {"id": 21, "name": "Sillamäe", "indicators": [8, 10, 11, 14, 16, 18, 20, 21, 23, 34, 37, 41]},
    33: {"id": 33, "name": "Tahkuse", "indicators": [1, 3, 6, 11, 68, 69]},
    38: {"id": 38, "name": "Sinimäe", "indicators": [1, 8, 11, 21, 23, 31, 34, 37, 41]},
    40: {"id": 40, "name": "VKG", "indicators": [1, 11, 34, 37, 41]},
    41: {"id": 41, "name": "Sillamäe 2", "indicators": [10, 34, 37, 41]},
    44: {"id": 44, "name": "Kiviõli", "indicators": [8, 11, 21, 34, 37, 41, 1]},
}

# Pollen Stations
POLLEN_STATIONS = {
    23: {"id": 23, "name": "Tallinn", "indicators": [48, 51, 59, 49, 57, 47, 62, 44]},
    25: {"id": 25, "name": "Tartu", "indicators": [48, 51, 59, 49, 57, 47, 62, 44]},
    27: {"id": 27, "name": "Pärnu", "indicators": [48, 51, 59, 49, 57, 47, 62, 44]},
    29: {"id": 29, "name": "Jõhvi", "indicators": [48, 51, 59, 49, 57, 47, 62, 44]},
    31: {"id": 31, "name": "Kuressaare", "indicators": [48, 51, 59, 49, 57, 47, 62, 44]},
}

# Radiation Stations
RADIATION_STATIONS = {
    45: {"id": 45, "name": "Kunda kiirgus", "indicators": [80]},
    46: {"id": 46, "name": "Kuusiku kiirgus", "indicators": [80]},
    47: {"id": 47, "name": "Lääne Nigula kiirgus", "indicators": [80]},
    48: {"id": 48, "name": "Mustvee kiirgus", "indicators": [80]},
    49: {"id": 49, "name": "Narva kiirgus", "indicators": [80]},
    50: {"id": 50, "name": "Pärnu kiirgus", "indicators": [80]},
    51: {"id": 51, "name": "Ristna kiirgus", "indicators": [80]},
    52: {"id": 52, "name": "Sõrve radiation", "indicators": [80]},
    53: {"id": 53, "name": "Tallinna kiirgus", "indicators": [80]},
    54: {"id": 54, "name": "Tõravere radiation", "indicators": [80]},
    55: {"id": 55, "name": "Türi radiation", "indicators": [80]},
    56: {"id": 56, "name": "Väike-Maarja kiirgus", "indicators": [80]},
    57: {"id": 57, "name": "Valga kiirgus", "indicators": [80]},
    58: {"id": 58, "name": "Võru radiation", "indicators": [80]},
    59: {"id": 59, "name": "Viljandi kiirgus", "indicators": [80]},
}

# Combined dictionaries for easier access
INDICATORS = {
    DATA_TYPE_AIR_QUALITY: AIR_QUALITY_INDICATORS,
    DATA_TYPE_POLLEN: POLLEN_INDICATORS,
    DATA_TYPE_RADIATION: RADIATION_INDICATORS,
}

STATIONS = {
    DATA_TYPE_AIR_QUALITY: AIR_QUALITY_STATIONS,
    DATA_TYPE_POLLEN: POLLEN_STATIONS,
    DATA_TYPE_RADIATION: RADIATION_STATIONS,
}
