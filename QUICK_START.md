# Quick Start Guide

Get started with the Crown Land Atlas tool in 5 minutes.

## Installation

```bash
# Clone the repository
git clone <your-repo-url>
cd crown-sync

# Install dependencies
pip install -r requirements.txt
```

## Your First Query

### Step 1: List Available Services

```bash
python -m __main__ list-services
```

This will show you all available services in the Crown Land Atlas.

### Step 2: Get Service Information

Once you've identified a service, get detailed information:

```bash
python -m __main__ service-info "ServiceName/MapServer"
```

Replace `ServiceName/MapServer` with an actual service name from step 1.

### Step 3: Get Layer Information

Check what data is available in a specific layer:

```bash
python -m __main__ layer-info "ServiceName/MapServer" 0
```

The `0` is the layer ID. You can find layer IDs from the service-info output.

### Step 4: Download Data

Download data as GeoJSON:

```bash
python -m __main__ query "ServiceName/MapServer" 0 \
    --output crown_land_data.geojson \
    --format geojson
```

Or as CSV (attributes only):

```bash
python -m __main__ query "ServiceName/MapServer" 0 \
    --output crown_land_data.csv \
    --format csv
```

## Filtering Data

Use SQL-like WHERE clauses to filter data:

```bash
# Get features where AREA is greater than 1000
python -m __main__ query "ServiceName/MapServer" 0 \
    --where "AREA > 1000" \
    --output large_areas.geojson

# Get features with specific name
python -m __main__ query "ServiceName/MapServer" 0 \
    --where "NAME LIKE '%Park%'" \
    --output parks.geojson
```

## Using in Python Scripts

```python
from crown_land_atlas import CrownLandAtlas

# Create client
client = CrownLandAtlas()

# List services
services = client.list_services()

# Query a layer
features = client.query_features(
    'ServiceName/MapServer',
    layer_id=0,
    where='1=1',
    out_fields='*'
)

# Export to GeoJSON
client.export_geojson(features, 'output.geojson')
```

## Common Use Cases

### Download All Crown Land Parcels

```bash
python -m __main__ query "CrownLand/MapServer" 0 \
    --where "1=1" \
    --output all_crown_land.geojson
```

### Get Protected Areas

```bash
python -m __main__ query "ProtectedAreas/MapServer" 0 \
    --where "STATUS = 'Protected'" \
    --output protected_areas.geojson
```

### Export Specific Fields Only

```bash
python -m __main__ query "ServiceName/MapServer" 0 \
    --fields "OBJECTID,NAME,AREA,TYPE" \
    --output selected_fields.csv \
    --format csv
```

### Change Coordinate System

```bash
# Output in WGS84 (EPSG:4326)
python -m __main__ query "ServiceName/MapServer" 0 \
    --out-sr 4326 \
    --output data_wgs84.geojson
```

## Troubleshooting

### Connection Errors

If you get connection errors, the API might be temporarily unavailable or have restrictions. The tool uses the official proxy URL, but some services may still be restricted.

### Large Datasets

For very large datasets, use:
- `--max-records` to limit the number of records
- Filter with `--where` clauses to reduce data size
- Export to CSV if you only need attributes (smaller files)

### Finding Service Names

The service names can be tricky. Use `list-services` to see all available options, and look for services ending in `/MapServer` or `/FeatureServer`.

## Next Steps

- Check out `examples/basic_usage.py` for Python API examples
- See `examples/discover_and_download.py` for a complete workflow
- Read the full README.md for advanced features

## Getting Help

For more information on any command:

```bash
python -m __main__ --help
python -m __main__ query --help
```
