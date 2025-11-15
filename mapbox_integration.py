#!/usr/bin/env python3
"""
Mapbox integration for Crown Land Atlas data.

This module handles uploading Crown Land data to Mapbox as tilesets
for use in web maps.
"""

import os
import json
import time
import requests
from typing import Dict, Optional, List
from pathlib import Path


class MapboxUploader:
    """Upload Crown Land data to Mapbox."""

    def __init__(self, access_token: Optional[str] = None):
        """
        Initialize Mapbox uploader.

        Args:
            access_token: Mapbox access token (if not provided, reads from MAPBOX_ACCESS_TOKEN env var)
        """
        self.access_token = access_token or os.getenv('MAPBOX_ACCESS_TOKEN')
        if not self.access_token:
            raise ValueError(
                "Mapbox access token required. Set MAPBOX_ACCESS_TOKEN environment variable "
                "or pass access_token parameter."
            )

        self.api_base = "https://api.mapbox.com"
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json'
        })

    def create_dataset(self, name: str, description: str = "") -> Dict:
        """
        Create a new Mapbox dataset.

        Args:
            name: Dataset name
            description: Dataset description

        Returns:
            Dataset information
        """
        url = f"{self.api_base}/datasets/v1/{self._get_username()}"
        params = {'access_token': self.access_token}
        data = {
            'name': name,
            'description': description
        }

        response = self.session.post(url, params=params, json=data)
        response.raise_for_status()
        return response.json()

    def list_datasets(self) -> List[Dict]:
        """
        List all datasets.

        Returns:
            List of datasets
        """
        url = f"{self.api_base}/datasets/v1/{self._get_username()}"
        params = {'access_token': self.access_token}

        response = self.session.get(url, params=params)
        response.raise_for_status()
        return response.json()

    def update_dataset(self, dataset_id: str, geojson: Dict) -> Dict:
        """
        Update a dataset with GeoJSON features.

        Args:
            dataset_id: ID of the dataset to update
            geojson: GeoJSON FeatureCollection

        Returns:
            Update result
        """
        # For large datasets, we need to upload features in batches
        features = geojson.get('features', [])

        if len(features) == 0:
            print("No features to upload")
            return {}

        print(f"Uploading {len(features)} features to dataset {dataset_id}...")

        # Mapbox Datasets API uses individual feature uploads
        # For large datasets, this can be slow - consider using Tilesets API instead
        uploaded = 0
        for feature in features:
            # Each feature needs a unique ID
            if 'id' not in feature:
                # Use OBJECTID or generate one
                feature['id'] = feature.get('properties', {}).get('OBJECTID', str(uploaded))

            url = f"{self.api_base}/datasets/v1/{self._get_username()}/{dataset_id}/features/{feature['id']}"
            params = {'access_token': self.access_token}

            response = self.session.put(url, params=params, json=feature)
            response.raise_for_status()

            uploaded += 1
            if uploaded % 100 == 0:
                print(f"  Uploaded {uploaded}/{len(features)} features...")

        print(f"Successfully uploaded {uploaded} features")
        return {'uploaded': uploaded}

    def upload_tileset(self, tileset_name: str, geojson_file: str) -> Dict:
        """
        Upload a GeoJSON file as a Mapbox tileset using the Uploads API.
        This is more efficient for large datasets than the Datasets API.

        Args:
            tileset_name: Name for the tileset (will be prefixed with username)
            geojson_file: Path to GeoJSON file

        Returns:
            Upload status
        """
        username = self._get_username()

        # Step 1: Get S3 credentials
        creds_url = f"{self.api_base}/uploads/v1/{username}/credentials"
        params = {'access_token': self.access_token}

        response = self.session.post(creds_url, params=params)
        response.raise_for_status()
        credentials = response.json()

        # Step 2: Upload file to S3
        print(f"Uploading {geojson_file} to S3...")
        s3_url = credentials['url']

        with open(geojson_file, 'rb') as f:
            files = {'file': f}
            s3_response = requests.post(
                s3_url,
                data=credentials['fields'],
                files=files
            )
            s3_response.raise_for_status()

        # Step 3: Create upload
        print(f"Creating tileset upload...")
        upload_url = f"{self.api_base}/uploads/v1/{username}"

        tileset_id = f"{username}.{tileset_name}"
        upload_data = {
            'url': credentials['url'] + credentials['key'],
            'tileset': tileset_id,
            'name': tileset_name
        }

        response = self.session.post(upload_url, params=params, json=upload_data)
        response.raise_for_status()
        upload_info = response.json()

        print(f"Upload started. Upload ID: {upload_info.get('id')}")
        print(f"Tileset ID: {tileset_id}")

        return upload_info

    def get_upload_status(self, upload_id: str) -> Dict:
        """
        Check the status of a tileset upload.

        Args:
            upload_id: Upload ID from upload_tileset

        Returns:
            Upload status information
        """
        username = self._get_username()
        url = f"{self.api_base}/uploads/v1/{username}/{upload_id}"
        params = {'access_token': self.access_token}

        response = self.session.get(url, params=params)
        response.raise_for_status()
        return response.json()

    def wait_for_upload(self, upload_id: str, timeout: int = 600) -> Dict:
        """
        Wait for an upload to complete.

        Args:
            upload_id: Upload ID
            timeout: Maximum time to wait in seconds

        Returns:
            Final upload status
        """
        start_time = time.time()

        while time.time() - start_time < timeout:
            status = self.get_upload_status(upload_id)
            progress = status.get('progress', 0)

            print(f"Upload progress: {progress}/1")

            if status.get('complete'):
                if status.get('error'):
                    raise Exception(f"Upload failed: {status.get('error')}")
                print("Upload complete!")
                return status

            time.sleep(5)

        raise TimeoutError(f"Upload did not complete within {timeout} seconds")

    def list_tilesets(self, limit: int = 100) -> List[Dict]:
        """
        List available tilesets.

        Args:
            limit: Maximum number of tilesets to return

        Returns:
            List of tilesets
        """
        username = self._get_username()
        url = f"{self.api_base}/tilesets/v1/{username}"
        params = {
            'access_token': self.access_token,
            'limit': limit
        }

        response = self.session.get(url, params=params)
        response.raise_for_status()
        return response.json()

    def get_tileset_info(self, tileset_id: str) -> Dict:
        """
        Get information about a tileset.

        Args:
            tileset_id: Tileset ID (e.g., 'username.tileset_name')

        Returns:
            Tileset information
        """
        url = f"{self.api_base}/tilesets/v1/{tileset_id}"
        params = {'access_token': self.access_token}

        response = self.session.get(url, params=params)
        response.raise_for_status()
        return response.json()

    def delete_tileset(self, tileset_id: str) -> bool:
        """
        Delete a tileset.

        Args:
            tileset_id: Tileset ID to delete

        Returns:
            True if successful
        """
        url = f"{self.api_base}/tilesets/v1/{tileset_id}"
        params = {'access_token': self.access_token}

        response = self.session.delete(url, params=params)
        response.raise_for_status()
        return True

    def _get_username(self) -> str:
        """
        Get the username associated with the access token.

        Returns:
            Mapbox username
        """
        # Extract username from token or make API call
        # For simplicity, we'll make an API call
        url = f"{self.api_base}/tokens/v2"
        params = {'access_token': self.access_token}

        response = self.session.get(url, params=params)
        response.raise_for_status()

        # The response contains token info
        # Username is typically in the token itself or we can get it from /v1/
        # Let's use a simpler approach - call the user endpoint
        url = "https://api.mapbox.com/v1"
        params = {'access_token': self.access_token}

        response = self.session.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        # Extract username from the API response
        return data.get('id') or data.get('username')

    def create_static_map_url(
        self,
        tileset_id: str,
        center_lon: float,
        center_lat: float,
        zoom: int = 10,
        width: int = 600,
        height: int = 400
    ) -> str:
        """
        Create a URL for a static map image.

        Args:
            tileset_id: Tileset ID
            center_lon: Center longitude
            center_lat: Center latitude
            zoom: Zoom level
            width: Image width
            height: Image height

        Returns:
            Static map URL
        """
        style = f"mapbox/streets-v11/static/{center_lon},{center_lat},{zoom}/{width}x{height}"
        url = f"https://api.mapbox.com/styles/v1/{style}"

        return f"{url}?access_token={self.access_token}"


def sync_crown_land_to_mapbox(
    service_name: str,
    layer_id: int,
    tileset_name: str,
    where: str = '1=1',
    access_token: Optional[str] = None
) -> Dict:
    """
    Convenience function to sync Crown Land data to Mapbox.

    Args:
        service_name: Crown Land service name
        layer_id: Layer ID
        tileset_name: Name for the Mapbox tileset
        where: SQL where clause for filtering
        access_token: Mapbox access token

    Returns:
        Upload status
    """
    from crown_land_atlas import CrownLandAtlas

    # Download data from Crown Land Atlas
    print("Downloading Crown Land data...")
    client = CrownLandAtlas()

    geojson = client.query_to_geojson(
        service_name,
        layer_id,
        where=where,
        out_sr=4326  # WGS84 for Mapbox
    )

    # Save to temporary file
    temp_file = f"{tileset_name}.geojson"
    with open(temp_file, 'w') as f:
        json.dump(geojson, f)

    print(f"Downloaded {len(geojson['features'])} features")

    # Upload to Mapbox
    print("Uploading to Mapbox...")
    uploader = MapboxUploader(access_token)

    upload_info = uploader.upload_tileset(tileset_name, temp_file)

    # Wait for upload to complete
    final_status = uploader.wait_for_upload(upload_info['id'])

    # Clean up temp file
    os.remove(temp_file)

    return final_status


if __name__ == '__main__':
    # Simple test
    uploader = MapboxUploader()
    try:
        tilesets = uploader.list_tilesets()
        print(f"Found {len(tilesets)} tilesets")
    except Exception as e:
        print(f"Error: {e}")
        print("Make sure MAPBOX_ACCESS_TOKEN environment variable is set")
