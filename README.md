# Estonian Ambient Air Quality

A Home Assistant integration that provides real-time and historical data from the Estonian Air Quality Monitoring System (https://ohuseire.ee).

## Features

- Monitors Estonian air quality, pollen, and radiation data
- Creates sensors for various indicators (PM10, PM2.5, CO, nitrogen dioxide, pollen types, radiation)
- Updates hourly from the official data source
- Automatically falls back to historical data for pollen when current data isn't available
- Compatible with Home Assistant's device classes for appropriate display of values

## Installation

### Method 1: HACS (Recommended)

1. Go to `HACS` -> `Integrations`
2. Select `...` from upper right corner
3. Select `Custom repositories`
4. Add https://github.com/zaifkhan/estonian_air_quality and select Type as `Integration`
5. Search for Estonian Ambient Air Quality and select it
6. Press `Download`
7. Restart Home Assistant

### Method 2: Manual Installation

1. Download the latest release from GitHub
2. Create a directory `custom_components/estonian_air_quality/` in your Home Assistant configuration directory
3. Extract the downloaded files into this directory
4. Restart Home Assistant

## Configuration

1. Go to Configuration → Devices & Services
2. Click "+ Add Integration" in the bottom right
3. Search for "Estonian Ambient Air Quality"
4. Follow the configuration steps:
   - Select which data types you want to monitor (Air Quality, Pollen, Radiation)
   - For each selected data type, choose a monitoring station
5. Click "Submit"

## Available Data Types

### Air Quality
Monitoring of various air quality indicators like:
- PM10 (Particulate Matter ≤10μm)
- PM2.5 (Particulate Matter ≤2.5μm)
- Sulphur dioxide (SO₂)
- Nitrogen dioxide (NO₂)
- Carbon monoxide (CO)
- Ozone (O₃)
- And more...

### Pollen
Data about various pollen types, including:
- Birch
- Alder
- Grasses
- Hazel
- Wormwood
- Juniper
- Saltbush
- Alternaria

### Radiation
Environmental radiation measurements across Estonia.

## Sensors

Sensors are grouped by domain:
- Air Quality sensors: `sensor.air_quality_*`
- Pollen sensors: `sensor.pollen_*`
- Radiation sensors: `sensor.radiation_*`

Each sensor provides:
- Current value with appropriate unit
- Station information
- Indicator details
- Measurement timestamps
- Formula and description details

For pollen sensors, additional attributes show when data was last updated and whether historical data is being used.

## Advanced Usage

### Attributes

Each sensor comes with rich attributes providing additional information:

```yaml
station_id: 23
station_name: Tallinn
indicator_id: 48
indicator_name: Birch
description: Birch is a thinleaved deciduous hardwood tree...
formula: null
data_type: pollen
original_unit: tk/m³
last_measured: 2025-03-19 00:00:00
last_checked: 2025-03-22 15:30:22
fetch_date: 19.03.2025
is_historical: true
last_successful_date: 19.03.2025
coordinator_last_checked: 22.03.2025
```

### Historical Data

For pollen data, if no data is available for the current day, the integration automatically:
1. Looks back up to 7 days for the most recent data
2. Uses that data until newer information becomes available
3. Continues checking hourly for updates
4. Clearly marks when historical data is being used through the `is_historical` attribute

## Troubleshooting

If you're encountering issues:

1. Check that you can access https://ohuseire.ee in your browser
2. Verify your internet connection is stable
3. Restart Home Assistant
4. Look at the Home Assistant logs for any error messages
5. If you see "No data available" for pollen sensors, this might be normal during off-seasons

## Credits

- Data source: [Estonian Air Quality Monitoring System](https://ohuseire.ee)
- This integration is not affiliated with or endorsed by the Estonian Environmental Research Centre

## License

[MIT License](LICENSE)

## Support

If you encounter any issues or have suggestions for improvements, please:
1. Check the [GitHub Issues](https://github.com/zaifkhan/estonian_air_quality/issues) page to see if your issue has already been reported
2. If not, open a new issue with a clear description and steps to reproduce

## Contributing

Contributions are welcome! Feel free to submit pull requests or suggest features/improvements.
