#!/usr/bin/env python3
"""
Diagnostic tool to test Crown Land Atlas API access.

This tool helps debug connection issues by trying different URL patterns
and proxy configurations.
"""

import requests
import json
from urllib.parse import urlencode, quote


def test_url(description, url, headers=None):
    """Test a URL and report the result."""
    print(f"\n{'='*60}")
    print(f"TEST: {description}")
    print(f"URL: {url}")
    if headers:
        print(f"Headers: {headers}")
    print('-' * 60)

    try:
        response = requests.get(url, headers=headers, timeout=30)
        print(f"Status Code: {response.status_code}")
        print(f"Content-Type: {response.headers.get('Content-Type', 'N/A')}")
        print(f"Content Length: {len(response.content)} bytes")

        if response.status_code == 200:
            print("✓ SUCCESS")
            try:
                data = response.json()
                print(f"Response preview: {json.dumps(data, indent=2)[:500]}...")
                return True, data
            except:
                print(f"Response preview: {response.text[:500]}...")
                return True, response.text
        else:
            print(f"✗ FAILED: {response.status_code} {response.reason}")
            print(f"Response: {response.text[:500]}")
            return False, None

    except Exception as e:
        print(f"✗ ERROR: {str(e)}")
        return False, None


def main():
    """Run diagnostic tests."""
    print("="*60)
    print("CROWN LAND ATLAS - DIAGNOSTIC TOOL")
    print("="*60)

    # Base URLs
    base_url = "https://intra.ws.lioservices.lrc.gov.on.ca/arcgis4/rest/services/CLUPA"
    proxy_base = "https://www.lioapplications.lrc.gov.on.ca/services/proxy/proxy.ashx"

    # Test 1: Direct access (will likely fail, but good to confirm)
    test_url(
        "Direct access without proxy",
        f"{base_url}?f=json"
    )

    # Test 2: Proxy with URL as query parameter
    test_url(
        "Proxy with URL parameter",
        f"{proxy_base}?{base_url}?f=json"
    )

    # Test 3: Proxy with URL encoded
    encoded_url = quote(f"{base_url}?f=json", safe='')
    test_url(
        "Proxy with encoded URL",
        f"{proxy_base}?{encoded_url}"
    )

    # Test 4: Proxy with url= parameter
    test_url(
        "Proxy with url= parameter",
        f"{proxy_base}?url={base_url}?f=json"
    )

    # Test 5: Proxy with encoded url= parameter
    test_url(
        "Proxy with url= parameter (encoded)",
        f"{proxy_base}?url={quote(f'{base_url}?f=json', safe='')}"
    )

    # Test 6: Different format parameter
    test_url(
        "Proxy with format at proxy level",
        f"{proxy_base}?{base_url}&f=json"
    )

    # Test 7: With common headers
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Referer': 'https://www.lioapplications.lrc.gov.on.ca/',
        'Accept': 'application/json, text/plain, */*'
    }
    test_url(
        "Proxy with browser-like headers",
        f"{proxy_base}?{base_url}?f=json",
        headers
    )

    # Test 8: Try a known working LIO service through proxy
    public_service = "https://ws.lioservices.lrc.gov.on.ca/arcgis1/rest/services"
    test_url(
        "Test proxy with public LIO service",
        f"{proxy_base}?{public_service}?f=json"
    )

    # Test 9: Try the public LIO services directly (no proxy)
    test_url(
        "Direct access to public LIO services",
        f"{public_service}?f=json"
    )

    # Test 10: Ontario GeoHub (alternative public access)
    test_url(
        "Ontario GeoHub services",
        "https://geohub.lio.gov.on.ca/api/v3/datasets?q=crown%20land"
    )

    print("\n" + "="*60)
    print("DIAGNOSTIC COMPLETE")
    print("="*60)
    print("\nNext steps:")
    print("1. If any test succeeded, note which URL pattern works")
    print("2. Check if you need to access from a specific IP/network")
    print("3. Look for alternative Ontario government data portals")
    print("4. Contact Ontario LIO support for API access details")
    print("\nUseful links:")
    print("- Ontario GeoHub: https://geohub.lio.gov.on.ca/")
    print("- Ontario Data Catalogue: https://data.ontario.ca/")
    print("- LIO Contact: https://www.ontario.ca/page/land-information-ontario")


if __name__ == '__main__':
    main()
