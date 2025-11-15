#!/usr/bin/env python3
"""
Sync Crown Land Atlas data to Mapbox.

This script downloads data from Ontario's Crown Land Atlas and uploads it
to Mapbox as a tileset for use in web maps.
"""

import argparse
import json
import sys
import os
from pathlib import Path
from crown_land_atlas import CrownLandAtlas
from mapbox_integration import MapboxUploader


def load_config(config_file: str) -> dict:
    """Load configuration from JSON file."""
    with open(config_file, 'r') as f:
        return json.load(f)


def save_config(config: dict, config_file: str):
    """Save configuration to JSON file."""
    with open(config_file, 'w') as f:
        json.dump(config, f, indent=2)


def sync_layer(
    service_name: str,
    layer_id: int,
    tileset_name: str,
    where: str = '1=1',
    access_token: str = None,
    max_records: int = None
):
    """
    Sync a single layer to Mapbox.

    Args:
        service_name: Crown Land service name
        layer_id: Layer ID
        tileset_name: Mapbox tileset name
        where: SQL where clause
        access_token: Mapbox access token
        max_records: Maximum records to download
    """
    print("=" * 60)
    print(f"SYNCING: {service_name}/{layer_id} -> {tileset_name}")
    print("=" * 60)

    # Step 1: Download from Crown Land Atlas
    print("\n[1/4] Downloading Crown Land data...")
    client = CrownLandAtlas()

    try:
        geojson = client.query_to_geojson(
            service_name,
            layer_id,
            where=where,
            out_sr=4326,  # WGS84 for Mapbox
            max_records=max_records
        )

        feature_count = len(geojson.get('features', []))
        print(f"✓ Downloaded {feature_count} features")

        if feature_count == 0:
            print("⚠ No features found. Aborting upload.")
            return None

    except Exception as e:
        print(f"✗ Error downloading data: {e}")
        return None

    # Step 2: Save to temporary file
    print("\n[2/4] Saving to temporary file...")
    temp_file = f"temp_{tileset_name}.geojson"

    try:
        with open(temp_file, 'w') as f:
            json.dump(geojson, f)

        file_size = os.path.getsize(temp_file) / (1024 * 1024)  # MB
        print(f"✓ Saved to {temp_file} ({file_size:.2f} MB)")

    except Exception as e:
        print(f"✗ Error saving file: {e}")
        return None

    # Step 3: Upload to Mapbox
    print("\n[3/4] Uploading to Mapbox...")

    try:
        uploader = MapboxUploader(access_token)
        upload_info = uploader.upload_tileset(tileset_name, temp_file)

        print(f"✓ Upload initiated")
        print(f"  Upload ID: {upload_info.get('id')}")
        print(f"  Tileset ID: {upload_info.get('tileset')}")

    except Exception as e:
        print(f"✗ Error uploading to Mapbox: {e}")
        # Clean up temp file
        if os.path.exists(temp_file):
            os.remove(temp_file)
        return None

    # Step 4: Wait for completion
    print("\n[4/4] Waiting for upload to complete...")

    try:
        final_status = uploader.wait_for_upload(upload_info['id'])

        print(f"✓ Upload complete!")
        print(f"  Tileset: {final_status.get('tileset')}")

        # Clean up temp file
        if os.path.exists(temp_file):
            os.remove(temp_file)
            print(f"✓ Cleaned up temporary file")

        return final_status

    except Exception as e:
        print(f"✗ Error during upload: {e}")
        # Clean up temp file
        if os.path.exists(temp_file):
            os.remove(temp_file)
        return None


def sync_from_config(config_file: str, access_token: str = None):
    """
    Sync multiple layers from a configuration file.

    Args:
        config_file: Path to JSON configuration file
        access_token: Mapbox access token (overrides config file)
    """
    print("Loading configuration...")
    config = load_config(config_file)

    # Get access token
    token = access_token or config.get('mapbox_access_token') or os.getenv('MAPBOX_ACCESS_TOKEN')
    if not token:
        print("Error: Mapbox access token not found.")
        print("Set MAPBOX_ACCESS_TOKEN environment variable or add it to config file.")
        sys.exit(1)

    layers = config.get('layers', [])
    if not layers:
        print("Error: No layers defined in configuration file.")
        sys.exit(1)

    print(f"Found {len(layers)} layer(s) to sync\n")

    results = []
    for i, layer in enumerate(layers, 1):
        print(f"\n{'='*60}")
        print(f"Layer {i}/{len(layers)}")
        print(f"{'='*60}")

        result = sync_layer(
            service_name=layer['service_name'],
            layer_id=layer['layer_id'],
            tileset_name=layer['tileset_name'],
            where=layer.get('where', '1=1'),
            access_token=token,
            max_records=layer.get('max_records')
        )

        results.append({
            'layer': layer['tileset_name'],
            'success': result is not None
        })

    # Summary
    print("\n" + "=" * 60)
    print("SYNC SUMMARY")
    print("=" * 60)

    success_count = sum(1 for r in results if r['success'])
    print(f"Successful: {success_count}/{len(results)}")

    for result in results:
        status = "✓" if result['success'] else "✗"
        print(f"{status} {result['layer']}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Sync Crown Land Atlas data to Mapbox'
    )

    parser.add_argument(
        '--config',
        help='Path to configuration file (JSON)'
    )

    parser.add_argument(
        '--service',
        help='Crown Land service name (e.g., ServiceName/MapServer)'
    )

    parser.add_argument(
        '--layer-id',
        type=int,
        help='Layer ID'
    )

    parser.add_argument(
        '--tileset-name',
        help='Mapbox tileset name'
    )

    parser.add_argument(
        '--where',
        default='1=1',
        help='SQL where clause (default: "1=1" for all records)'
    )

    parser.add_argument(
        '--max-records',
        type=int,
        help='Maximum number of records to download'
    )

    parser.add_argument(
        '--access-token',
        help='Mapbox access token (or set MAPBOX_ACCESS_TOKEN env var)'
    )

    args = parser.parse_args()

    # Mode 1: Sync from config file
    if args.config:
        sync_from_config(args.config, args.access_token)

    # Mode 2: Sync single layer
    elif args.service and args.layer_id is not None and args.tileset_name:
        token = args.access_token or os.getenv('MAPBOX_ACCESS_TOKEN')
        if not token:
            print("Error: Mapbox access token required.")
            print("Set MAPBOX_ACCESS_TOKEN environment variable or use --access-token")
            sys.exit(1)

        sync_layer(
            service_name=args.service,
            layer_id=args.layer_id,
            tileset_name=args.tileset_name,
            where=args.where,
            access_token=token,
            max_records=args.max_records
        )

    else:
        print("Error: Either --config or (--service, --layer-id, --tileset-name) required")
        parser.print_help()
        sys.exit(1)


if __name__ == '__main__':
    main()
