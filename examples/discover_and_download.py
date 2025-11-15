#!/usr/bin/env python3
"""
Example script showing how to discover services and download data.

This script demonstrates a complete workflow:
1. List all services
2. Explore a service to find layers
3. Get layer information
4. Download data from a layer
"""

import sys
import os
import json

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from crown_land_atlas import CrownLandAtlas


def explore_services(client):
    """Explore available services."""
    print("\n" + "=" * 60)
    print("DISCOVERING SERVICES")
    print("=" * 60)

    try:
        catalog = client.list_services()

        # Show folders
        folders = catalog.get('folders', [])
        if folders:
            print(f"\nFolders ({len(folders)}):")
            for folder in folders:
                print(f"  - {folder}")

        # Show services
        services = catalog.get('services', [])
        if services:
            print(f"\nServices ({len(services)}):")
            for service in services:
                name = service.get('name', 'Unknown')
                service_type = service.get('type', 'Unknown')
                print(f"  - {name} ({service_type})")

        return services

    except Exception as e:
        print(f"Error listing services: {e}")
        return []


def explore_service(client, service_name):
    """Explore a specific service."""
    print("\n" + "=" * 60)
    print(f"EXPLORING SERVICE: {service_name}")
    print("=" * 60)

    try:
        info = client.get_service_info(service_name)

        print(f"\nService Name: {info.get('mapName', 'N/A')}")
        print(f"Description: {info.get('description', 'N/A')}")
        print(f"Service Description: {info.get('serviceDescription', 'N/A')}")

        # Show layers
        layers = info.get('layers', [])
        if layers:
            print(f"\nLayers ({len(layers)}):")
            for layer in layers:
                layer_id = layer.get('id')
                layer_name = layer.get('name', 'Unknown')
                print(f"  [{layer_id}] {layer_name}")

        return layers

    except Exception as e:
        print(f"Error getting service info: {e}")
        return []


def explore_layer(client, service_name, layer_id):
    """Explore a specific layer."""
    print("\n" + "=" * 60)
    print(f"EXPLORING LAYER: {service_name}/{layer_id}")
    print("=" * 60)

    try:
        layer_info = client.get_layer_info(service_name, layer_id)

        print(f"\nName: {layer_info.get('name', 'N/A')}")
        print(f"Description: {layer_info.get('description', 'N/A')}")
        print(f"Geometry Type: {layer_info.get('geometryType', 'N/A')}")
        print(f"Min Scale: {layer_info.get('minScale', 'N/A')}")
        print(f"Max Scale: {layer_info.get('maxScale', 'N/A')}")

        # Show fields
        fields = layer_info.get('fields', [])
        if fields:
            print(f"\nFields ({len(fields)}):")
            for field in fields[:10]:  # Show first 10 fields
                field_name = field.get('name')
                field_type = field.get('type')
                field_alias = field.get('alias', field_name)
                print(f"  - {field_name} ({field_type}) - {field_alias}")

            if len(fields) > 10:
                print(f"  ... and {len(fields) - 10} more fields")

        # Show extent
        extent = layer_info.get('extent', {})
        if extent:
            print(f"\nExtent:")
            print(f"  xmin: {extent.get('xmin')}")
            print(f"  ymin: {extent.get('ymin')}")
            print(f"  xmax: {extent.get('xmax')}")
            print(f"  ymax: {extent.get('ymax')}")
            print(f"  Spatial Reference: {extent.get('spatialReference', {}).get('wkid')}")

        return layer_info

    except Exception as e:
        print(f"Error getting layer info: {e}")
        return None


def download_layer_data(client, service_name, layer_id, output_prefix='data'):
    """Download data from a layer."""
    print("\n" + "=" * 60)
    print(f"DOWNLOADING DATA: {service_name}/{layer_id}")
    print("=" * 60)

    try:
        # Download as GeoJSON
        print("\nDownloading as GeoJSON...")
        geojson = client.query_to_geojson(
            service_name,
            layer_id,
            where='1=1',  # Get all features
            out_sr=4326   # WGS84 coordinate system
        )

        geojson_file = f"{output_prefix}.geojson"
        with open(geojson_file, 'w') as f:
            json.dump(geojson, f, indent=2)

        feature_count = len(geojson.get('features', []))
        print(f"  Saved {feature_count} features to {geojson_file}")

        # Download as CSV
        print("\nDownloading attributes as CSV...")
        features = client.query_features(
            service_name,
            layer_id,
            where='1=1',
            return_geometry=False
        )

        csv_file = f"{output_prefix}.csv"
        client.export_csv(features, csv_file)

        return True

    except Exception as e:
        print(f"Error downloading data: {e}")
        return False


def main():
    """Main workflow."""
    print("=" * 60)
    print("CROWN LAND ATLAS - DISCOVERY AND DOWNLOAD TOOL")
    print("=" * 60)

    # Initialize client
    client = CrownLandAtlas()

    # Step 1: Discover services
    services = explore_services(client)

    if not services:
        print("\nNo services found or error occurred.")
        print("The API may be restricted or require authentication.")
        return

    # Interactive mode: let user choose a service
    print("\n" + "=" * 60)
    print("To explore a specific service, modify this script and set:")
    print("  - SERVICE_NAME: The name of the service (e.g., 'MyService/MapServer')")
    print("  - LAYER_ID: The ID of the layer to download")
    print("=" * 60)

    # Example (uncomment and modify to use):
    # SERVICE_NAME = "YourService/MapServer"
    # LAYER_ID = 0
    #
    # # Step 2: Explore the service
    # layers = explore_service(client, SERVICE_NAME)
    #
    # # Step 3: Explore a specific layer
    # if layers:
    #     layer_info = explore_layer(client, SERVICE_NAME, LAYER_ID)
    #
    #     # Step 4: Download the data
    #     if layer_info:
    #         output_name = f"crown_land_layer_{LAYER_ID}"
    #         success = download_layer_data(client, SERVICE_NAME, LAYER_ID, output_name)
    #
    #         if success:
    #             print("\n" + "=" * 60)
    #             print("DOWNLOAD COMPLETE!")
    #             print("=" * 60)


if __name__ == '__main__':
    main()
