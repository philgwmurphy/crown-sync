#!/usr/bin/env python3
"""
Alternative data access through Ontario Data Catalogue.

If direct API access is restricted, this module provides access to Crown Land
data through Ontario's open data portal.
"""

import requests
import json
from typing import Dict, List, Optional


class OntarioDataCatalogue:
    """Access Crown Land data through Ontario Data Catalogue."""

    def __init__(self):
        """Initialize the client."""
        self.base_url = "https://data.ontario.ca/api/3/action"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Crown-Land-Atlas-Tool/1.0'
        })

    def search_datasets(self, query: str = "crown land") -> List[Dict]:
        """
        Search for datasets in the catalogue.

        Args:
            query: Search query

        Returns:
            List of matching datasets
        """
        url = f"{self.base_url}/package_search"
        params = {
            'q': query,
            'rows': 100
        }

        response = self.session.get(url, params=params)
        response.raise_for_status()

        data = response.json()
        if data.get('success'):
            return data['result']['results']
        return []

    def get_dataset(self, dataset_id: str) -> Dict:
        """
        Get details about a specific dataset.

        Args:
            dataset_id: Dataset identifier

        Returns:
            Dataset information
        """
        url = f"{self.base_url}/package_show"
        params = {'id': dataset_id}

        response = self.session.get(url, params=params)
        response.raise_for_status()

        data = response.json()
        if data.get('success'):
            return data['result']
        return {}

    def list_crown_land_datasets(self) -> List[Dict]:
        """
        List all Crown Land related datasets.

        Returns:
            List of Crown Land datasets
        """
        queries = [
            "crown land",
            "Crown Land Use Policy Atlas",
            "CLUPA",
            "ontario parks",
            "public land"
        ]

        all_datasets = []
        seen_ids = set()

        for query in queries:
            datasets = self.search_datasets(query)
            for ds in datasets:
                if ds['id'] not in seen_ids:
                    all_datasets.append(ds)
                    seen_ids.add(ds['id'])

        return all_datasets

    def get_download_urls(self, dataset_id: str) -> List[Dict]:
        """
        Get download URLs for a dataset.

        Args:
            dataset_id: Dataset identifier

        Returns:
            List of resources with download URLs
        """
        dataset = self.get_dataset(dataset_id)
        resources = []

        for resource in dataset.get('resources', []):
            resources.append({
                'name': resource.get('name'),
                'format': resource.get('format'),
                'url': resource.get('url'),
                'size': resource.get('size'),
                'description': resource.get('description')
            })

        return resources

    def download_resource(self, url: str, output_file: str):
        """
        Download a resource file.

        Args:
            url: Resource URL
            output_file: Output file path
        """
        print(f"Downloading {url}...")

        response = self.session.get(url, stream=True)
        response.raise_for_status()

        total_size = int(response.headers.get('content-length', 0))
        downloaded = 0

        with open(output_file, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    if total_size > 0:
                        percent = (downloaded / total_size) * 100
                        print(f"\rProgress: {percent:.1f}%", end='')

        print(f"\n✓ Downloaded to {output_file}")


def find_crown_land_data():
    """Helper function to find Crown Land data."""
    client = OntarioDataCatalogue()

    print("Searching Ontario Data Catalogue for Crown Land data...")
    datasets = client.list_crown_land_datasets()

    print(f"\nFound {len(datasets)} datasets:\n")

    for i, ds in enumerate(datasets, 1):
        print(f"{i}. {ds['title']}")
        print(f"   ID: {ds['name']}")
        print(f"   URL: https://data.ontario.ca/dataset/{ds['name']}")

        # Get resources
        resources = client.get_download_urls(ds['id'])
        if resources:
            print(f"   Resources ({len(resources)}):")
            for res in resources[:3]:  # Show first 3
                print(f"     - {res['name']} ({res['format']})")
        print()

    return datasets


if __name__ == '__main__':
    find_crown_land_data()
