#!/usr/bin/env python3
"""
Example script demonstrating basic usage of the Crown Land Atlas tool.
"""

import sys
import os

# Add parent directory to path to import the module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from crown_land_atlas import CrownLandAtlas


def main():
    """Demonstrate basic usage."""
    # Initialize the client
    client = CrownLandAtlas()

    print("=" * 60)
    print("Ontario Crown Land Atlas - Example Usage")
    print("=" * 60)

    # Example 1: List available services
    print("\n1. Listing available services...")
    try:
        services = client.list_services()
        print(f"   Found {len(services.get('services', []))} services")
        print(f"   Found {len(services.get('folders', []))} folders")

        # Print service names
        for service in services.get('services', [])[:5]:  # First 5 only
            print(f"   - {service.get('name')} ({service.get('type')})")

        if len(services.get('services', [])) > 5:
            print(f"   ... and {len(services.get('services', [])) - 5} more")

    except Exception as e:
        print(f"   Error: {e}")

    # Example 2: Get service information
    # Note: Replace 'YourService/MapServer' with an actual service name
    print("\n2. Getting service information...")
    print("   (Uncomment and modify the service name to test)")
    # try:
    #     service_name = "YourService/MapServer"
    #     info = client.get_service_info(service_name)
    #     print(f"   Service: {info.get('mapName')}")
    #     print(f"   Description: {info.get('description', 'N/A')}")
    #     print(f"   Number of layers: {len(info.get('layers', []))}")
    # except Exception as e:
    #     print(f"   Error: {e}")

    # Example 3: Get layer information
    print("\n3. Getting layer information...")
    print("   (Uncomment and modify the service/layer to test)")
    # try:
    #     service_name = "YourService/MapServer"
    #     layer_id = 0
    #     layer_info = client.get_layer_info(service_name, layer_id)
    #     print(f"   Layer: {layer_info.get('name')}")
    #     print(f"   Geometry Type: {layer_info.get('geometryType')}")
    #     print(f"   Feature Count: {layer_info.get('count', 'Unknown')}")
    # except Exception as e:
    #     print(f"   Error: {e}")

    # Example 4: Query features
    print("\n4. Querying features...")
    print("   (Uncomment and modify to test)")
    # try:
    #     service_name = "YourService/MapServer"
    #     layer_id = 0
    #
    #     # Query all features
    #     features = client.query_features(
    #         service_name,
    #         layer_id,
    #         where='1=1',
    #         out_fields='*',
    #         return_geometry=True,
    #         max_records=10  # Limit to 10 for example
    #     )
    #
    #     print(f"   Retrieved {len(features)} features")
    #
    #     # Export to GeoJSON
    #     client.export_geojson(features, 'output.geojson')
    #     print(f"   Exported to output.geojson")
    #
    # except Exception as e:
    #     print(f"   Error: {e}")

    # Example 5: Query with filters
    print("\n5. Querying with attribute filters...")
    print("   (Uncomment and modify to test)")
    # try:
    #     service_name = "YourService/MapServer"
    #     layer_id = 0
    #
    #     # Query with a where clause
    #     # Example: where="AREA > 1000" or where="NAME LIKE '%Park%'"
    #     features = client.query_features(
    #         service_name,
    #         layer_id,
    #         where="YOUR_FIELD = 'YOUR_VALUE'",
    #         out_fields='*',
    #         return_geometry=True
    #     )
    #
    #     print(f"   Retrieved {len(features)} filtered features")
    #
    # except Exception as e:
    #     print(f"   Error: {e}")

    # Example 6: Export to different formats
    print("\n6. Exporting to different formats...")
    print("   (Uncomment and modify to test)")
    # try:
    #     service_name = "YourService/MapServer"
    #     layer_id = 0
    #
    #     features = client.query_features(
    #         service_name,
    #         layer_id,
    #         where='1=1',
    #         max_records=100
    #     )
    #
    #     # Export as GeoJSON
    #     client.export_geojson(features, 'data.geojson')
    #
    #     # Export as CSV (attributes only)
    #     client.export_csv(features, 'data.csv')
    #
    #     print(f"   Exported to data.geojson and data.csv")
    #
    # except Exception as e:
    #     print(f"   Error: {e}")

    print("\n" + "=" * 60)
    print("Example completed!")
    print("Uncomment the examples above and modify service names to test.")
    print("=" * 60)


if __name__ == '__main__':
    main()
