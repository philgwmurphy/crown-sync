# Crown Land Atlas Tool

A Python tool to access and download public data from Ontario's Crown Land Use Policy Atlas (CLUPA).

## Overview

This tool provides a simple interface to query and download geospatial data from Ontario's Crown Land Atlas ArcGIS REST services through the official proxy.

## Features

### Data Access
- Discover available map services and feature layers
- Query feature data with spatial and attribute filters
- Export data in multiple formats (GeoJSON, CSV)
- Handle pagination for large datasets
- Command-line interface for easy access

### Mapbox Integration
- Sync Crown Land data to Mapbox tilesets
- Interactive web map viewer
- Automated updates via cron, GitHub Actions, or systemd
- Real-time data visualization

## Installation

```bash
pip install -r requirements.txt
```

## ⚠️ IMPORTANT: API Access Issue

**The default API endpoint is INTERNAL-ONLY and won't work from the public internet.**

The hostname `intra.ws.lioservices.lrc.gov.on.ca` is only accessible from Ontario government networks. You'll get DNS resolution errors or 403 Forbidden.

### ✅ What Works - Use These Instead:

1. **Ontario Data Catalogue** (easiest):
   ```bash
   python ontario_data_catalogue.py
   ```
   Download Crown Land datasets from https://data.ontario.ca/

2. **Public LIO Services**:
   ```bash
   python public_ontario_data.py
   ```
   Access public map services at `ws.lioservices.lrc.gov.on.ca`

3. **Ontario GeoHub**: https://geohub.lio.gov.on.ca/
   Browse and download data through web interface

**See [API_ACCESS_EXPLAINED.md](API_ACCESS_EXPLAINED.md) for complete details.**

## Usage

### Python API

```python
from crown_land_atlas import CrownLandAtlas

# Initialize client
client = CrownLandAtlas()

# List available services
services = client.list_services()
print(services)

# Get layer information
layer_info = client.get_layer_info('ServiceName/MapServer', layer_id=0)

# Query features
features = client.query_features(
    'ServiceName/MapServer',
    layer_id=0,
    where='1=1',  # SQL where clause
    out_fields='*',
    return_geometry=True
)

# Export to GeoJSON
client.export_geojson(features, 'output.geojson')
```

### Command Line

```bash
# List all services
python -m crown_land_atlas list-services

# Get layer info
python -m crown_land_atlas layer-info "ServiceName/MapServer" --layer-id 0

# Query and export data
python -m crown_land_atlas query "ServiceName/MapServer" \
    --layer-id 0 \
    --where "1=1" \
    --output data.geojson \
    --format geojson
```

## API Endpoints

### Internal (Not Publicly Accessible)
- Base Service URL: `https://intra.ws.lioservices.lrc.gov.on.ca/arcgis4/rest/services/CLUPA`
- **Note:** The `intra.` subdomain is internal-only and requires Ontario government network access

### Public Alternatives
- Public LIO Services: `https://ws.lioservices.lrc.gov.on.ca/arcgis1/rest/services`
- Ontario Data Catalogue: `https://data.ontario.ca/`
- Ontario GeoHub: `https://geohub.lio.gov.on.ca/`

Use the public alternatives or download datasets from the data catalogue.

## Mapbox Integration

Automatically sync Crown Land data to Mapbox for interactive web maps.

### Quick Start with Mapbox

1. **Get a Mapbox account** at https://account.mapbox.com/

2. **Set your access token:**
   ```bash
   export MAPBOX_ACCESS_TOKEN="sk.your_secret_token_here"
   ```

3. **Create a configuration file:**
   ```bash
   cp config.example.json config.json
   # Edit config.json with your layer settings
   ```

4. **Sync data to Mapbox:**
   ```bash
   python sync_to_mapbox.py --config config.json
   ```

5. **Set up the web viewer:**
   ```bash
   cd web
   cp config.example.js config.js
   # Edit config.js with your public token and tilesets
   python3 -m http.server 8000
   # Open http://localhost:8000
   ```

### Automated Updates

Keep your map data fresh with automated syncing:

- **Cron (Linux/Mac):** `cd automation && ./setup_cron.sh`
- **GitHub Actions:** Copy `automation/github_actions.yml` to `.github/workflows/`
- **Windows:** Use Task Scheduler with `automation/sync_cron.bat`

See [automation/README.md](automation/README.md) for detailed setup instructions.

## Project Structure

```
crown-sync/
├── crown_land_atlas.py        # Core API client
├── mapbox_integration.py      # Mapbox upload functionality
├── sync_to_mapbox.py          # Sync script
├── config.example.json        # Configuration template
├── web/                       # Web map viewer
│   ├── index.html            # Map interface
│   ├── config.example.js     # Viewer configuration
│   └── README.md             # Viewer documentation
├── automation/               # Automation scripts
│   ├── sync_cron.sh         # Cron sync script
│   ├── setup_cron.sh        # Cron setup helper
│   ├── github_actions.yml   # GitHub Actions workflow
│   └── README.md            # Automation guide
└── examples/                # Usage examples
    ├── basic_usage.py
    └── discover_and_download.py
```

## Documentation

- [Quick Start Guide](QUICK_START.md) - Get started in 5 minutes
- [Web Viewer Guide](web/README.md) - Set up the interactive map
- [Automation Guide](automation/README.md) - Schedule automatic updates

## License

MIT
