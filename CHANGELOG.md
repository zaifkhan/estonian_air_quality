# Changelog

## v1.1.0 (2025-04-06)

### Fixed
- Improved error handling for API connection failures
- Fixed encoding issues with API responses
- Enhanced reliability of data fetching from the Estonian Air Quality API
- Fixed date handling in historical data fallbacks
- Fixed attribute naming issues in sensor entities

### Added
- Retry mechanism (3 attempts) for handling transient API errors
- Extended data fetch window from 1 to 3 days for more reliable data
- Multiple encoding fallbacks (UTF-8 and Latin-1)
- Force update service for manually refreshing air quality data
- Additional diagnostic attributes (API status, response codes)
- Improved sensor icons based on data type

### Changed
- More resilient data handling to maintain state during API outages
- Enhanced logging with detailed diagnostic information
- Better entity availability tracking to prevent "unavailable" state
- More graceful handling of component setup when API is temporarily down

## v1.0.0 (2025-03-15)

### Initial Release
- First public release of the Estonian Ambient Air Quality integration
- Support for air quality, pollen, and radiation monitoring
- Automatic fallback to historical data when current data is unavailable
- Integration with Home Assistant's device classes for appropriate display
