# Crown Land Atlas Tool

A Python tool to access and download public data from Ontario's Crown Land Use Policy Atlas (CLUPA).

## Overview

This tool provides a simple interface to query and download geospatial data from Ontario's Crown Land Atlas ArcGIS REST services through the official proxy.

## Features

- Discover available map services and feature layers
- Query feature data with spatial and attribute filters
- Export data in multiple formats (GeoJSON, CSV)
- Handle pagination for large datasets
- Command-line interface for easy access

## Installation

```bash
pip install -r requirements.txt
```

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

- Base Service URL: `https://intra.ws.lioservices.lrc.gov.on.ca/arcgis4/rest/services/CLUPA`
- Proxy URL: `https://www.lioapplications.lrc.gov.on.ca/services/proxy/proxy.ashx?`

All requests are routed through the proxy to access the internal services.

## License

MIT
