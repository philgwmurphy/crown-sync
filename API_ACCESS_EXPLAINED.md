# API Access Issue Explained

## The Problem

The URL you were given uses an **internal-only domain** that's not accessible from the public internet:

```
https://intra.ws.lioservices.lrc.gov.on.ca/arcgis4/rest/services/CLUPA
         ^^^^^
         This means "internal" - not public!
```

### DNS Resolution Failure

Your error shows:
```
Failed to resolve 'intra.ws.lioservices.lrc.gov.on.ca'
```

This hostname **doesn't exist in public DNS**. It's only accessible:
- From within Ontario government networks
- Through a VPN connected to their internal network
- With special network configuration/whitelisting

## The Solution

You have several options to access Crown Land data:

### Option 1: Use Ontario Data Catalogue (Recommended)

Download datasets directly from Ontario's open data portal:

```bash
python ontario_data_catalogue.py
```

This will show you available Crown Land datasets you can download.

**Example:**
```python
from ontario_data_catalogue import OntarioDataCatalogue

client = OntarioDataCatalogue()
datasets = client.search_datasets("crown land")

for ds in datasets:
    print(f"{ds['title']}")
    print(f"  Download: https://data.ontario.ca/dataset/{ds['name']}")
```

**Advantages:**
- ✓ Publicly accessible
- ✓ No authentication needed
- ✓ Official government data
- ✓ Various formats (GeoJSON, Shapefile, etc.)

**Website:** https://data.ontario.ca/

### Option 2: Use Public LIO Services

Access public-facing Ontario map services:

```bash
python public_ontario_data.py
```

This uses the **public** endpoint:
```
https://ws.lioservices.lrc.gov.on.ca/arcgis1/rest/services
        ^^  (no "intra" - publicly accessible!)
```

**Example:**
```python
from public_ontario_data import PublicOntarioData

client = PublicOntarioData()

# List available public services
services = client.list_public_services()

# Find Crown Land related data
results = client.find_crown_land_services()

for item in results:
    print(f"{item['name']} [{item['source']}]")
```

### Option 3: Ontario GeoHub

Browse and download data through the web interface:

**Website:** https://geohub.lio.gov.on.ca/

1. Search for "Crown Land"
2. Browse datasets
3. Download in your preferred format
4. Use with Mapbox integration

### Option 4: Request API Access

If you need programmatic access to the CLUPA API:

**Contact:** Land Information Ontario (LIO)
- Email: lio.infoline@ontario.ca
- Website: https://www.ontario.ca/page/land-information-ontario

**Request:**
- API credentials for CLUPA
- Documentation
- Network access details (if IP whitelisting is needed)

## Recommended Workflow

Here's how to use this tool with publicly accessible data:

### 1. Find Available Data

```bash
# Search Ontario Data Catalogue
python ontario_data_catalogue.py

# OR explore public services
python public_ontario_data.py
```

### 2. Download Data

**Option A: Download via script**
```python
from ontario_data_catalogue import OntarioDataCatalogue

client = OntarioDataCatalogue()

# Find Crown Land dataset
datasets = client.search_datasets("crown land use policy atlas")

if datasets:
    # Get download URLs for first result
    resources = client.get_download_urls(datasets[0]['id'])

    # Download GeoJSON or Shapefile
    for res in resources:
        if res['format'] in ['GEOJSON', 'SHP', 'GDB']:
            print(f"Downloading {res['name']}...")
            client.download_resource(res['url'], f"crown_land.{res['format'].lower()}")
```

**Option B: Download manually**
1. Visit https://data.ontario.ca/
2. Search "Crown Land Use Policy Atlas"
3. Download the dataset
4. Save as `crown_land.geojson`

### 3. Upload to Mapbox

Once you have the data file:

```bash
# Set your Mapbox token
export MAPBOX_ACCESS_TOKEN="sk.your_token"

# Upload to Mapbox
python -c "from mapbox_integration import MapboxUploader; \
           u = MapboxUploader(); \
           u.upload_tileset('crown_land', 'crown_land.geojson')"
```

### 4. Set Up Web Viewer

```bash
cd web
cp config.example.js config.js
# Edit config.js with your tileset name
python3 -m http.server 8000
```

### 5. Automate Updates (Optional)

If you find a public API endpoint or download URL that works:

1. Edit `config.json` to use the public service
2. Set up automation (GitHub Actions, cron, etc.)
3. Data syncs automatically

## Why This Happened

The URLs you were given are from internal documentation or tools meant for Ontario government employees. They work from:

- Ontario government office networks
- Government VPN connections
- Whitelisted IP addresses

This is common with government data systems that have both:
- **Internal APIs** (intra.*) - for staff use
- **Public APIs** (ws.*) - for public access
- **Open Data Portals** (data.ontario.ca) - for downloads

## What To Do Next

1. **Run the public data explorer:**
   ```bash
   python public_ontario_data.py
   ```

2. **Search the data catalogue:**
   ```bash
   python ontario_data_catalogue.py
   ```

3. **Pick a dataset and download it**

4. **Use the Mapbox integration** to visualize it

5. **Contact LIO** if you need real-time API access

## Common Public Datasets

Look for these on data.ontario.ca:

- **Crown Land Use Policy Atlas (CLUPA)**
- **Ontario Parks**
- **Conservation Reserves**
- **Provincial Parks Regulated**
- **Public Lands**
- **Forest Resources Inventory**

These are typically available as:
- GeoJSON (best for web maps)
- Shapefile (for GIS software)
- GDB (ArcGIS format)
- KML (Google Earth)

## Summary

✗ **Won't work:** `intra.ws.lioservices...` (internal only)

✓ **Will work:**
- `data.ontario.ca` (download datasets)
- `ws.lioservices...` (public API)
- `geohub.lio.gov.on.ca` (browse and download)
- Contact LIO for official API access

The tool is ready to use - you just need to point it at publicly accessible data sources!
