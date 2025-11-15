# Troubleshooting Guide

## 403 Forbidden Error

If you're getting a `403 Forbidden` error when accessing the Crown Land Atlas API, this is a common issue. Here are the causes and solutions:

### Cause 1: API Access Restrictions

The Crown Land Use Policy Atlas API may have access restrictions:
- IP-based restrictions (only accessible from within Ontario government network)
- Authentication requirements
- Referrer checks
- Rate limiting

### Solution 1: Run the Diagnostic Tool

```bash
python diagnostics.py
```

This will test various URL patterns and configurations to identify what works.

### Solution 2: Use Ontario Data Catalogue (Alternative)

Ontario provides open data through their data catalogue which doesn't require special access:

```bash
python ontario_data_catalogue.py
```

This will search for Crown Land datasets available for public download.

#### Example: Finding Crown Land Data

```python
from ontario_data_catalogue import OntarioDataCatalogue

client = OntarioDataCatalogue()

# Search for Crown Land datasets
datasets = client.search_datasets("crown land")

for ds in datasets:
    print(f"{ds['title']}")
    print(f"  URL: https://data.ontario.ca/dataset/{ds['name']}")

    # Get download links
    resources = client.get_download_urls(ds['id'])
    for res in resources:
        print(f"  - {res['name']} ({res['format']}): {res['url']}")
```

### Solution 3: Contact Ontario LIO

If you need real-time API access:

1. **Contact Land Information Ontario (LIO)**
   - Website: https://www.ontario.ca/page/land-information-ontario
   - Email: lio.infoline@ontario.ca
   - Request API access credentials

2. **Request Information:**
   - Explain your use case
   - Ask about API access requirements
   - Request documentation for the CLUPA API

### Solution 4: Use Web Services

Ontario provides several web service endpoints:

1. **Ontario GeoHub**
   - URL: https://geohub.lio.gov.on.ca/
   - Browse Crown Land datasets
   - Download in various formats

2. **Make Ontario**
   - URL: https://www.ontario.ca/page/make-ontario
   - Official mapping application
   - May provide alternative data access

3. **ArcGIS Online Services**
   - Some layers may be available through ArcGIS Online
   - Search: https://www.arcgis.com/home/search.html?q=ontario%20crown%20land

## Other Common Issues

### Issue: ModuleNotFoundError

**Error:** `ModuleNotFoundError: No module named 'requests'`

**Solution:**
```bash
pip install -r requirements.txt
```

### Issue: SSL Certificate Error

**Error:** `SSL: CERTIFICATE_VERIFY_FAILED`

**Solution:**
```python
# Temporary workaround (not recommended for production)
import ssl
ssl._create_default_https_context = ssl._create_unverified_context
```

### Issue: Timeout Errors

**Error:** `ReadTimeout` or `ConnectTimeout`

**Solution:**
```python
# Increase timeout in crown_land_atlas.py
client = CrownLandAtlas(timeout=60)  # 60 seconds
```

### Issue: Empty Response

**Error:** Got 200 OK but no data

**Solution:**
- Check if the service/layer exists
- Verify the `where` clause syntax
- Try with `where='1=1'` to get all records

## Alternative Data Sources

If the API remains inaccessible, consider these alternatives:

### 1. Download Static Datasets

Visit Ontario Data Catalogue and download datasets manually:
```
https://data.ontario.ca/
```

Search for:
- "Crown Land Use Policy Atlas"
- "Ontario Parks"
- "Public Lands"

### 2. Use Existing Datasets

Pre-processed Crown Land data may be available from:
- Ontario GeoHub
- Open Data portals
- Academic institutions
- Third-party GIS data providers

### 3. Web Scraping (Last Resort)

If official APIs aren't available, you might need to:
1. Use the Make Ontario web interface
2. Capture network requests
3. Reverse engineer the data access method

**Note:** Always respect terms of service and robots.txt

## Getting Help

### Check Logs

```bash
# For sync script
tail -f logs/crown-sync.log

# For web server
# Check browser console (F12)
```

### Debug Mode

Add debug output to your scripts:

```python
import logging

logging.basicConfig(level=logging.DEBUG)
```

### Report Issues

If you've tried everything:

1. Run diagnostics: `python diagnostics.py`
2. Collect error messages
3. Note your location/network
4. Create an issue with details

## Network-Specific Issues

### Corporate/University Network

Some networks block external API access:
- Try from a different network
- Use a VPN
- Contact your IT department

### Government Network

The API might only work from within Ontario government network:
- Request access from LIO
- Use alternative data sources
- Work with a government partner

## Rate Limiting

If you're getting intermittent 403s:
- Add delays between requests
- Reduce concurrent requests
- Respect rate limits

```python
import time

# Add delay between requests
time.sleep(1)  # 1 second delay
```

## Data Quality Issues

### Incorrect Geometry

If geometries are wrong:
- Check spatial reference (should be 4326 for WGS84)
- Verify coordinate order (longitude, latitude)
- Check for geometry simplification

### Missing Attributes

If fields are missing:
- Use `out_fields='*'` to get all fields
- Check layer definition for available fields
- Some fields may be restricted

## Mapbox Upload Issues

### Upload Fails

If Mapbox upload fails:
- Check file size (max 300MB for GeoJSON)
- Verify token has upload permissions
- Check Mapbox service status

### Upload Stuck

If processing never completes:
- Wait up to 30 minutes for large datasets
- Check Mapbox Studio for status
- Try uploading a smaller dataset first

## Need More Help?

1. **Ontario LIO Support:** lio.infoline@ontario.ca
2. **Mapbox Support:** https://support.mapbox.com/
3. **Project Issues:** Create an issue in this repository
4. **Community:** GIS Stack Exchange, Reddit r/gis
