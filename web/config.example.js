// Mapbox configuration
// Copy this file to config.js and fill in your values

const CONFIG = {
    // Your Mapbox public access token
    MAPBOX_ACCESS_TOKEN: 'pk.YOUR_MAPBOX_PUBLIC_TOKEN_HERE',

    // Your Mapbox username
    MAPBOX_USERNAME: 'your-username',

    // Default map center (longitude, latitude) - Ontario
    DEFAULT_CENTER: [-84.5, 49.5],

    // Default zoom level
    DEFAULT_ZOOM: 5,

    // Layers to display
    LAYERS: [
        {
            // Tileset name (must match what you uploaded)
            tileset_name: 'crown_land_parcels',

            // Display name
            name: 'Crown Land Parcels',

            // Geometry type: 'polygon', 'line', or 'point'
            geometry_type: 'polygon',

            // Layer color (hex code)
            color: '#2E7D32',

            // Visible by default
            visible: true,

            // Fields to show in popup (optional, shows all if not specified)
            popup_fields: ['OBJECTID', 'NAME', 'AREA', 'TYPE', 'STATUS']
        },
        {
            tileset_name: 'protected_areas',
            name: 'Protected Areas',
            geometry_type: 'polygon',
            color: '#FFA726',
            visible: true,
            popup_fields: ['NAME', 'STATUS', 'AREA']
        }
        // Add more layers here
    ]
};
