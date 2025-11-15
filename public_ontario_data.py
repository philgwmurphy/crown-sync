#!/usr/bin/env python3
"""
Access publicly available Ontario geospatial data.

This module uses public-facing Ontario data services that don't require
special network access or authentication.
"""

import json
import requests
from typing import Dict, List, Optional


class PublicOntarioData:
    """Access public Ontario geospatial data services."""

    def __init__(self, timeout: int = 30):
        """
        Initialize the client.

        Args:
            timeout: Request timeout in seconds
        """
        # Public-facing LIO services (not intra.)
        self.public_lio_base = "https://ws.lioservices.lrc.gov.on.ca/arcgis1/rest/services"
        self.geohub_api = "https://geohub.lio.gov.on.ca/api/v3"

        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json, text/plain, */*'
        })

    def list_public_services(self) -> Dict:
        """
        List public LIO ArcGIS services.

        Returns:
            Dictionary containing service information
        """
        url = f"{self.public_lio_base}?f=json"

        try:
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            raise Exception(f"Failed to list services: {e}")

    def get_service_info(self, service_path: str) -> Dict:
        """
        Get information about a specific service.

        Args:
            service_path: Service path (e.g., 'LIO_OPEN/LIO_Open/MapServer')

        Returns:
            Service metadata
        """
        url = f"{self.public_lio_base}/{service_path}?f=json"

        try:
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            raise Exception(f"Failed to get service info: {e}")

    def get_layer_info(self, service_path: str, layer_id: int) -> Dict:
        """
        Get information about a layer.

        Args:
            service_path: Service path
            layer_id: Layer ID

        Returns:
            Layer metadata
        """
        url = f"{self.public_lio_base}/{service_path}/{layer_id}?f=json"

        try:
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            raise Exception(f"Failed to get layer info: {e}")

    def query_layer(
        self,
        service_path: str,
        layer_id: int,
        where: str = '1=1',
        out_fields: str = '*',
        return_geometry: bool = True,
        out_sr: int = 4326,
        result_record_count: int = 1000
    ) -> List[Dict]:
        """
        Query features from a layer.

        Args:
            service_path: Service path
            layer_id: Layer ID
            where: SQL where clause
            out_fields: Fields to return
            return_geometry: Include geometry
            out_sr: Output spatial reference (4326 = WGS84)
            result_record_count: Records per request

        Returns:
            List of features
        """
        url = f"{self.public_lio_base}/{service_path}/{layer_id}/query"

        all_features = []
        offset = 0

        while True:
            params = {
                'where': where,
                'outFields': out_fields,
                'returnGeometry': 'true' if return_geometry else 'false',
                'outSR': out_sr,
                'f': 'json',
                'resultOffset': offset,
                'resultRecordCount': result_record_count
            }

            try:
                response = self.session.get(url, params=params, timeout=self.timeout)
                response.raise_for_status()
                data = response.json()

                if 'error' in data:
                    raise Exception(f"Query error: {data['error'].get('message', 'Unknown')}")

                features = data.get('features', [])
                if not features:
                    break

                all_features.extend(features)

                # Check if there are more records
                if not data.get('exceededTransferLimit', False):
                    break

                offset += len(features)

            except Exception as e:
                raise Exception(f"Failed to query layer: {e}")

        return all_features

    def search_geohub(self, query: str = "crown land") -> List[Dict]:
        """
        Search Ontario GeoHub for datasets.

        Args:
            query: Search query

        Returns:
            List of matching datasets
        """
        url = f"{self.geohub_api}/datasets"
        params = {'q': query}

        try:
            response = self.session.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            raise Exception(f"Failed to search GeoHub: {e}")

    def find_crown_land_services(self) -> List[Dict]:
        """
        Find publicly accessible Crown Land related services.

        Returns:
            List of relevant services
        """
        results = []

        print("Searching public Ontario services...")

        # Check public LIO services
        try:
            services = self.list_public_services()

            # Look for folders/services related to Crown Land, Parks, etc.
            for folder in services.get('folders', []):
                if any(keyword in folder.lower() for keyword in ['land', 'park', 'conservation', 'natural']):
                    results.append({
                        'type': 'folder',
                        'name': folder,
                        'source': 'public_lio'
                    })

            for service in services.get('services', []):
                name = service.get('name', '')
                if any(keyword in name.lower() for keyword in ['land', 'park', 'conservation', 'open', 'public']):
                    results.append({
                        'type': 'service',
                        'name': name,
                        'service_type': service.get('type'),
                        'source': 'public_lio'
                    })

        except Exception as e:
            print(f"Could not access public LIO services: {e}")

        # Check GeoHub
        try:
            datasets = self.search_geohub("crown land")
            for ds in datasets[:10]:  # Limit to first 10
                results.append({
                    'type': 'dataset',
                    'name': ds.get('title'),
                    'id': ds.get('id'),
                    'source': 'geohub'
                })
        except Exception as e:
            print(f"Could not access GeoHub: {e}")

        return results


def explore_public_data():
    """Explore publicly available Crown Land data."""
    client = PublicOntarioData()

    print("="*60)
    print("EXPLORING PUBLIC ONTARIO DATA SOURCES")
    print("="*60)

    # List all public services
    print("\n[1/3] Checking public LIO services...")
    try:
        services = client.list_public_services()

        print(f"\nFound {len(services.get('folders', []))} folders")
        for folder in services.get('folders', [])[:10]:
            print(f"  - {folder}/")

        print(f"\nFound {len(services.get('services', []))} services")
        for service in services.get('services', [])[:10]:
            print(f"  - {service.get('name')} ({service.get('type')})")

        if len(services.get('services', [])) > 10:
            print(f"  ... and {len(services.get('services', [])) - 10} more")

    except Exception as e:
        print(f"[ERROR] {e}")

    # Search for Crown Land data
    print("\n[2/3] Searching for Crown Land data...")
    try:
        results = client.find_crown_land_services()

        if results:
            print(f"\nFound {len(results)} relevant items:")
            for item in results[:20]:
                source = item.get('source', 'unknown')
                name = item.get('name', 'Unknown')
                print(f"  [{source}] {name}")
        else:
            print("No Crown Land specific services found")

    except Exception as e:
        print(f"[ERROR] {e}")

    # Try Ontario Data Catalogue
    print("\n[3/3] Checking Ontario Data Catalogue...")
    try:
        from ontario_data_catalogue import OntarioDataCatalogue

        cat_client = OntarioDataCatalogue()
        datasets = cat_client.search_datasets("crown land")

        print(f"\nFound {len(datasets)} datasets:")
        for ds in datasets[:5]:
            print(f"  - {ds['title']}")
            print(f"    URL: https://data.ontario.ca/dataset/{ds['name']}")

        if len(datasets) > 5:
            print(f"  ... and {len(datasets) - 5} more")

    except Exception as e:
        print(f"[ERROR] {e}")

    print("\n" + "="*60)
    print("RECOMMENDATIONS")
    print("="*60)
    print("\n1. The 'intra.ws' domain is INTERNAL ONLY - not publicly accessible")
    print("2. Use 'ws.lioservices.lrc.gov.on.ca' for public data")
    print("3. Download datasets from data.ontario.ca")
    print("4. Contact lio.infoline@ontario.ca for API access")
    print("\nFor Crown Land data specifically:")
    print("- Search: https://data.ontario.ca/ for 'Crown Land'")
    print("- Browse: https://geohub.lio.gov.on.ca/")
    print("- Map viewer: https://www.ontario.ca/page/make-ontario")


if __name__ == '__main__':
    explore_public_data()
