#!/usr/bin/env python3
"""
Ontario Crown Land Use Policy Atlas (CLUPA) API Client

This module provides tools to access geospatial data from Ontario's
Crown Land Atlas ArcGIS REST services.
"""

import json
import time
from typing import Dict, List, Optional, Any
from urllib.parse import urljoin, urlencode
import requests


class CrownLandAtlas:
    """Client for accessing Ontario Crown Land Atlas data."""

    BASE_URL = "https://intra.ws.lioservices.lrc.gov.on.ca/arcgis4/rest/services/CLUPA"
    PROXY_URL = "https://www.lioapplications.lrc.gov.on.ca/services/proxy/proxy.ashx?"

    def __init__(self, timeout: int = 30):
        """
        Initialize the Crown Land Atlas client.

        Args:
            timeout: Request timeout in seconds
        """
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Crown-Land-Atlas-Tool/1.0'
        })

    def _build_url(self, endpoint: str, params: Optional[Dict] = None) -> str:
        """
        Build a complete URL using the proxy.

        Args:
            endpoint: The service endpoint path
            params: Query parameters to include in the target URL

        Returns:
            Complete proxied URL
        """
        from urllib.parse import urlencode

        if endpoint.startswith('http'):
            full_url = endpoint
        else:
            # Remove leading slash if present
            endpoint = endpoint.lstrip('/')
            full_url = f"{self.BASE_URL}/{endpoint}"

        # Add parameters to the target URL before proxying
        if params:
            param_str = urlencode(params)
            full_url = f"{full_url}?{param_str}"

        # Construct proxy URL
        return f"{self.PROXY_URL}{full_url}"

    def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Dict:
        """
        Make a request to the ArcGIS REST API.

        Args:
            endpoint: API endpoint
            params: Query parameters

        Returns:
            JSON response as dictionary
        """
        if params is None:
            params = {}

        # Ensure JSON format for response
        params['f'] = 'json'

        # Build URL with params embedded (they need to be part of the proxied URL)
        url = self._build_url(endpoint, params)

        # Add browser-like headers to avoid being blocked
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Referer': 'https://www.lioapplications.lrc.gov.on.ca/'
        }

        try:
            # Don't pass params again since they're already in the URL
            response = self.session.get(url, headers=headers, timeout=self.timeout)
            response.raise_for_status()

            data = response.json()

            # Check for ArcGIS error responses
            if 'error' in data:
                error_msg = data['error'].get('message', 'Unknown error')
                raise Exception(f"ArcGIS API Error: {error_msg}")

            return data

        except requests.exceptions.RequestException as e:
            raise Exception(f"Request failed: {str(e)}")

    def list_services(self) -> Dict:
        """
        List all available services in the CLUPA catalog.

        Returns:
            Dictionary containing service information
        """
        return self._make_request('')

    def get_service_info(self, service_name: str) -> Dict:
        """
        Get information about a specific service.

        Args:
            service_name: Name of the service (e.g., 'MyService/MapServer')

        Returns:
            Service metadata and layer information
        """
        return self._make_request(service_name)

    def get_layer_info(self, service_name: str, layer_id: int) -> Dict:
        """
        Get information about a specific layer.

        Args:
            service_name: Name of the service
            layer_id: ID of the layer

        Returns:
            Layer metadata including fields, geometry type, etc.
        """
        endpoint = f"{service_name}/{layer_id}"
        return self._make_request(endpoint)

    def query_features(
        self,
        service_name: str,
        layer_id: int,
        where: str = '1=1',
        out_fields: str = '*',
        return_geometry: bool = True,
        geometry_precision: int = 6,
        out_sr: Optional[int] = None,
        max_records: Optional[int] = None
    ) -> List[Dict]:
        """
        Query features from a layer.

        Args:
            service_name: Name of the service
            layer_id: ID of the layer
            where: SQL where clause for filtering (default: '1=1' returns all)
            out_fields: Comma-separated list of fields to return (default: '*' for all)
            return_geometry: Whether to include geometry in results
            geometry_precision: Number of decimal places for coordinates
            out_sr: Output spatial reference WKID (e.g., 4326 for WGS84)
            max_records: Maximum number of records to return

        Returns:
            List of features
        """
        endpoint = f"{service_name}/{layer_id}/query"

        params = {
            'where': where,
            'outFields': out_fields,
            'returnGeometry': 'true' if return_geometry else 'false',
            'geometryPrecision': geometry_precision,
        }

        if out_sr:
            params['outSR'] = out_sr

        # Handle pagination for large datasets
        all_features = []
        offset = 0
        result_record_count = 1000  # Default batch size

        while True:
            params['resultOffset'] = offset

            if max_records:
                remaining = max_records - len(all_features)
                params['resultRecordCount'] = min(result_record_count, remaining)
                if remaining <= 0:
                    break

            result = self._make_request(endpoint, params)

            features = result.get('features', [])
            if not features:
                break

            all_features.extend(features)

            # Check if there are more records
            if not result.get('exceededTransferLimit', False):
                break

            offset += len(features)

            # Respect server limits
            time.sleep(0.1)

        return all_features

    def query_to_geojson(
        self,
        service_name: str,
        layer_id: int,
        where: str = '1=1',
        out_fields: str = '*',
        **kwargs
    ) -> Dict:
        """
        Query features and convert to GeoJSON format.

        Args:
            service_name: Name of the service
            layer_id: ID of the layer
            where: SQL where clause
            out_fields: Fields to include
            **kwargs: Additional arguments passed to query_features

        Returns:
            GeoJSON FeatureCollection
        """
        features = self.query_features(
            service_name,
            layer_id,
            where=where,
            out_fields=out_fields,
            return_geometry=True,
            **kwargs
        )

        return self._esri_to_geojson(features)

    def _esri_to_geojson(self, esri_features: List[Dict]) -> Dict:
        """
        Convert ESRI JSON features to GeoJSON.

        Args:
            esri_features: List of ESRI JSON features

        Returns:
            GeoJSON FeatureCollection
        """
        geojson_features = []

        for feature in esri_features:
            geojson_feature = {
                'type': 'Feature',
                'properties': feature.get('attributes', {}),
                'geometry': self._convert_geometry(feature.get('geometry', {}))
            }
            geojson_features.append(geojson_feature)

        return {
            'type': 'FeatureCollection',
            'features': geojson_features
        }

    def _convert_geometry(self, esri_geometry: Dict) -> Optional[Dict]:
        """
        Convert ESRI geometry to GeoJSON geometry.

        Args:
            esri_geometry: ESRI geometry object

        Returns:
            GeoJSON geometry object
        """
        if not esri_geometry:
            return None

        # Point
        if 'x' in esri_geometry and 'y' in esri_geometry:
            return {
                'type': 'Point',
                'coordinates': [esri_geometry['x'], esri_geometry['y']]
            }

        # Polyline
        if 'paths' in esri_geometry:
            if len(esri_geometry['paths']) == 1:
                return {
                    'type': 'LineString',
                    'coordinates': esri_geometry['paths'][0]
                }
            else:
                return {
                    'type': 'MultiLineString',
                    'coordinates': esri_geometry['paths']
                }

        # Polygon
        if 'rings' in esri_geometry:
            # Simple polygon
            if len(esri_geometry['rings']) == 1:
                return {
                    'type': 'Polygon',
                    'coordinates': esri_geometry['rings']
                }
            else:
                # Multi-polygon or polygon with holes
                # This is simplified - proper handling would check ring orientation
                return {
                    'type': 'Polygon',
                    'coordinates': esri_geometry['rings']
                }

        return None

    def export_geojson(self, features_or_geojson: Any, output_file: str):
        """
        Export features to a GeoJSON file.

        Args:
            features_or_geojson: Either ESRI features or GeoJSON FeatureCollection
            output_file: Path to output file
        """
        # Check if already GeoJSON
        if isinstance(features_or_geojson, dict) and features_or_geojson.get('type') == 'FeatureCollection':
            geojson = features_or_geojson
        else:
            geojson = self._esri_to_geojson(features_or_geojson)

        with open(output_file, 'w') as f:
            json.dump(geojson, f, indent=2)

        print(f"Exported {len(geojson['features'])} features to {output_file}")

    def export_csv(self, features: List[Dict], output_file: str):
        """
        Export features to CSV file.

        Args:
            features: List of ESRI features
            output_file: Path to output file
        """
        import csv

        if not features:
            print("No features to export")
            return

        # Get all unique field names
        fieldnames = set()
        for feature in features:
            fieldnames.update(feature.get('attributes', {}).keys())

        fieldnames = sorted(fieldnames)

        with open(output_file, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()

            for feature in features:
                writer.writerow(feature.get('attributes', {}))

        print(f"Exported {len(features)} features to {output_file}")


if __name__ == '__main__':
    # Simple test
    client = CrownLandAtlas()
    try:
        services = client.list_services()
        print(json.dumps(services, indent=2))
    except Exception as e:
        print(f"Error: {e}")
