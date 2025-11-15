#!/usr/bin/env python3
"""
Command-line interface for Crown Land Atlas tool.
"""

import argparse
import json
import sys
from crown_land_atlas import CrownLandAtlas


def cmd_list_services(args):
    """List all available services."""
    client = CrownLandAtlas()
    try:
        services = client.list_services()
        print(json.dumps(services, indent=2))
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_service_info(args):
    """Get information about a service."""
    client = CrownLandAtlas()
    try:
        info = client.get_service_info(args.service)
        print(json.dumps(info, indent=2))
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_layer_info(args):
    """Get information about a layer."""
    client = CrownLandAtlas()
    try:
        info = client.get_layer_info(args.service, args.layer_id)
        print(json.dumps(info, indent=2))
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_query(args):
    """Query features from a layer."""
    client = CrownLandAtlas()
    try:
        print(f"Querying {args.service} layer {args.layer_id}...")

        if args.format == 'geojson':
            geojson = client.query_to_geojson(
                args.service,
                args.layer_id,
                where=args.where,
                out_fields=args.fields,
                out_sr=args.out_sr,
                max_records=args.max_records
            )

            if args.output:
                with open(args.output, 'w') as f:
                    json.dump(geojson, f, indent=2)
                print(f"Exported {len(geojson['features'])} features to {args.output}")
            else:
                print(json.dumps(geojson, indent=2))

        elif args.format == 'csv':
            features = client.query_features(
                args.service,
                args.layer_id,
                where=args.where,
                out_fields=args.fields,
                return_geometry=False,
                max_records=args.max_records
            )

            if args.output:
                client.export_csv(features, args.output)
            else:
                print("CSV format requires --output parameter")
                sys.exit(1)

        else:  # json
            features = client.query_features(
                args.service,
                args.layer_id,
                where=args.where,
                out_fields=args.fields,
                out_sr=args.out_sr,
                max_records=args.max_records
            )

            result = {'features': features}

            if args.output:
                with open(args.output, 'w') as f:
                    json.dump(result, f, indent=2)
                print(f"Exported {len(features)} features to {args.output}")
            else:
                print(json.dumps(result, indent=2))

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    """Main entry point for CLI."""
    parser = argparse.ArgumentParser(
        description='Ontario Crown Land Atlas data access tool'
    )

    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    subparsers.required = True

    # list-services command
    parser_list = subparsers.add_parser(
        'list-services',
        help='List all available services'
    )
    parser_list.set_defaults(func=cmd_list_services)

    # service-info command
    parser_service = subparsers.add_parser(
        'service-info',
        help='Get information about a service'
    )
    parser_service.add_argument('service', help='Service name (e.g., MyService/MapServer)')
    parser_service.set_defaults(func=cmd_service_info)

    # layer-info command
    parser_layer = subparsers.add_parser(
        'layer-info',
        help='Get information about a layer'
    )
    parser_layer.add_argument('service', help='Service name')
    parser_layer.add_argument('layer_id', type=int, help='Layer ID')
    parser_layer.set_defaults(func=cmd_layer_info)

    # query command
    parser_query = subparsers.add_parser(
        'query',
        help='Query features from a layer'
    )
    parser_query.add_argument('service', help='Service name')
    parser_query.add_argument('layer_id', type=int, help='Layer ID')
    parser_query.add_argument(
        '--where',
        default='1=1',
        help='SQL where clause (default: "1=1" for all records)'
    )
    parser_query.add_argument(
        '--fields',
        default='*',
        help='Comma-separated list of fields to return (default: "*" for all)'
    )
    parser_query.add_argument(
        '--format',
        choices=['json', 'geojson', 'csv'],
        default='geojson',
        help='Output format (default: geojson)'
    )
    parser_query.add_argument(
        '--output',
        help='Output file path'
    )
    parser_query.add_argument(
        '--out-sr',
        type=int,
        help='Output spatial reference WKID (e.g., 4326 for WGS84)'
    )
    parser_query.add_argument(
        '--max-records',
        type=int,
        help='Maximum number of records to return'
    )
    parser_query.set_defaults(func=cmd_query)

    # Parse arguments and execute command
    args = parser.parse_args()
    args.func(args)


if __name__ == '__main__':
    main()
