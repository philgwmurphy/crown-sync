#!/usr/bin/env python3
"""
Process locally downloaded Crown Land data for Mapbox integration.

Since Ontario's APIs have restrictions, this tool helps you work with
data files you've downloaded manually from their websites.
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, List
import zipfile
import shutil


class LocalDataProcessor:
    """Process locally downloaded Crown Land data."""

    def __init__(self):
        """Initialize processor."""
        self.supported_formats = {
            'geojson': ['.geojson', '.json'],
            'shapefile': ['.shp', '.zip'],
            'gdb': ['.gdb', '.zip'],
            'kml': ['.kml', '.kmz']
        }

    def find_data_files(self, directory: str = '.') -> Dict[str, List[str]]:
        """
        Find geospatial data files in a directory.

        Args:
            directory: Directory to search

        Returns:
            Dictionary of files by format
        """
        files_by_format = {
            'geojson': [],
            'shapefile': [],
            'gdb': [],
            'kml': [],
            'unknown': []
        }

        for root, dirs, files in os.walk(directory):
            for file in files:
                filepath = os.path.join(root, file)
                ext = Path(file).suffix.lower()

                categorized = False
                for format_type, extensions in self.supported_formats.items():
                    if ext in extensions:
                        files_by_format[format_type].append(filepath)
                        categorized = True
                        break

                if not categorized and ext in ['.dbf', '.prj', '.shx']:
                    # Shapefile component
                    continue
                elif not categorized and ext:
                    files_by_format['unknown'].append(filepath)

        return files_by_format

    def validate_geojson(self, filepath: str) -> bool:
        """
        Validate a GeoJSON file.

        Args:
            filepath: Path to GeoJSON file

        Returns:
            True if valid
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)

            if data.get('type') != 'FeatureCollection':
                print(f"Warning: Not a FeatureCollection (found {data.get('type')})")
                return False

            features = data.get('features', [])
            if not features:
                print(f"Warning: No features found")
                return False

            print(f"Valid GeoJSON with {len(features)} features")
            return True

        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON - {e}")
            return False
        except Exception as e:
            print(f"Error: {e}")
            return False

    def extract_zip(self, zip_path: str, output_dir: str = None) -> str:
        """
        Extract a ZIP archive.

        Args:
            zip_path: Path to ZIP file
            output_dir: Output directory (auto-generated if not provided)

        Returns:
            Path to extraction directory
        """
        if output_dir is None:
            output_dir = zip_path.replace('.zip', '_extracted')

        os.makedirs(output_dir, exist_ok=True)

        print(f"Extracting {zip_path}...")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(output_dir)

        print(f"Extracted to {output_dir}")
        return output_dir

    def prepare_for_mapbox(self, input_file: str, output_file: str = None) -> str:
        """
        Prepare a data file for Mapbox upload.

        Args:
            input_file: Input file path
            output_file: Output GeoJSON file path

        Returns:
            Path to prepared file
        """
        if output_file is None:
            output_file = input_file.replace(Path(input_file).suffix, '_mapbox.geojson')

        ext = Path(input_file).suffix.lower()

        # If already GeoJSON, validate and optionally copy
        if ext in ['.geojson', '.json']:
            print(f"Validating {input_file}...")
            if self.validate_geojson(input_file):
                if input_file != output_file:
                    shutil.copy(input_file, output_file)
                    print(f"Copied to {output_file}")
                return output_file
            else:
                raise Exception("Invalid GeoJSON file")

        # For shapefiles, need ogr2ogr (GDAL)
        elif ext == '.shp':
            print(f"Converting Shapefile to GeoJSON...")
            print("Note: This requires GDAL/ogr2ogr to be installed")
            print("Install with: apt-get install gdal-bin (Linux) or brew install gdal (Mac)")
            print(f"\nRun this command:")
            print(f"  ogr2ogr -f GeoJSON {output_file} {input_file}")
            return None

        else:
            print(f"Unsupported format: {ext}")
            print("Supported formats: .geojson, .json, .shp (with GDAL)")
            return None


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description='Process locally downloaded Crown Land data'
    )

    parser.add_argument(
        'command',
        choices=['find', 'validate', 'prepare', 'upload'],
        help='Command to execute'
    )

    parser.add_argument(
        '--input',
        help='Input file or directory'
    )

    parser.add_argument(
        '--output',
        help='Output file'
    )

    parser.add_argument(
        '--tileset-name',
        help='Mapbox tileset name'
    )

    args = parser.parse_args()

    processor = LocalDataProcessor()

    if args.command == 'find':
        # Find data files
        directory = args.input or '.'
        print(f"Searching for data files in: {directory}")
        print("="*60)

        files = processor.find_data_files(directory)

        for format_type, file_list in files.items():
            if file_list:
                print(f"\n{format_type.upper()} files ({len(file_list)}):")
                for f in file_list:
                    size = os.path.getsize(f) / (1024 * 1024)
                    print(f"  - {f} ({size:.2f} MB)")

    elif args.command == 'validate':
        # Validate GeoJSON
        if not args.input:
            print("Error: --input required")
            sys.exit(1)

        print(f"Validating: {args.input}")
        print("="*60)

        if processor.validate_geojson(args.input):
            print("\n[SUCCESS] File is valid and ready for Mapbox")
        else:
            print("\n[FAILED] File has issues")
            sys.exit(1)

    elif args.command == 'prepare':
        # Prepare for Mapbox
        if not args.input:
            print("Error: --input required")
            sys.exit(1)

        print(f"Preparing: {args.input}")
        print("="*60)

        output = processor.prepare_for_mapbox(args.input, args.output)
        if output:
            print(f"\n[SUCCESS] Ready for upload: {output}")
        else:
            print("\n[FAILED] Could not prepare file")
            sys.exit(1)

    elif args.command == 'upload':
        # Upload to Mapbox
        if not args.input:
            print("Error: --input required")
            sys.exit(1)

        if not args.tileset_name:
            print("Error: --tileset-name required")
            sys.exit(1)

        print(f"Uploading: {args.input}")
        print(f"Tileset: {args.tileset_name}")
        print("="*60)

        # Validate first
        if not processor.validate_geojson(args.input):
            print("\n[FAILED] Invalid GeoJSON file")
            sys.exit(1)

        # Upload to Mapbox
        try:
            from mapbox_integration import MapboxUploader

            uploader = MapboxUploader()
            upload_info = uploader.upload_tileset(args.tileset_name, args.input)

            print(f"\n[SUCCESS] Upload initiated")
            print(f"Upload ID: {upload_info.get('id')}")
            print(f"Tileset ID: {upload_info.get('tileset')}")

            # Wait for completion
            final_status = uploader.wait_for_upload(upload_info['id'])
            print(f"\n[SUCCESS] Upload complete!")

        except Exception as e:
            print(f"\n[FAILED] Upload error: {e}")
            sys.exit(1)


if __name__ == '__main__':
    if len(sys.argv) == 1:
        # No arguments - show quick guide
        print("="*60)
        print("LOCAL DATA PROCESSOR")
        print("="*60)
        print("\nWork with manually downloaded Crown Land data files")
        print("\nCommands:")
        print("  find     - Find data files in a directory")
        print("  validate - Validate a GeoJSON file")
        print("  prepare  - Prepare a file for Mapbox")
        print("  upload   - Upload to Mapbox")
        print("\nExamples:")
        print("  python local_data.py find --input downloads/")
        print("  python local_data.py validate --input crown_land.geojson")
        print("  python local_data.py upload --input crown_land.geojson --tileset-name crown_land")
        print("\nFor more info: python local_data.py --help")
        print("")
    else:
        main()
