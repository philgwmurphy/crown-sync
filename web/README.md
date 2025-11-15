# Crown Land Atlas Web Viewer

A web-based map viewer for Ontario Crown Land data using Mapbox GL JS.

## Setup

1. **Copy the configuration template:**
   ```bash
   cd web
   cp config.example.js config.js
   ```

2. **Edit config.js with your settings:**
   - Add your Mapbox public access token
   - Add your Mapbox username
   - Configure layers to match your uploaded tilesets
   - Adjust default center and zoom for your area of interest

3. **Serve the files:**

   Option A: Python HTTP server
   ```bash
   python3 -m http.server 8000
   ```

   Option B: Node.js http-server
   ```bash
   npx http-server -p 8000
   ```

   Option C: Any web server (Apache, Nginx, etc.)

4. **Open in browser:**
   ```
   http://localhost:8000
   ```

## Configuration

### Mapbox Access Token

Get a token from: https://account.mapbox.com/access-tokens/

You need a **public token** (starts with `pk.`) for the web viewer.

### Layer Configuration

Each layer in the `LAYERS` array supports:

- `tileset_name`: Name of the tileset uploaded to Mapbox
- `name`: Display name shown in the layer controls
- `geometry_type`: Type of geometry ('polygon', 'line', or 'point')
- `color`: Hex color code for styling
- `visible`: Whether layer is visible by default (true/false)
- `popup_fields`: Array of field names to show in popups

### Example Configuration

```javascript
const CONFIG = {
    MAPBOX_ACCESS_TOKEN: 'pk.eyJ1IjoieW91ciIsInR5cCI6IkpXVCJ9...',
    MAPBOX_USERNAME: 'yourname',
    DEFAULT_CENTER: [-79.3832, 43.6532], // Toronto
    DEFAULT_ZOOM: 8,
    LAYERS: [
        {
            tileset_name: 'crown_land_parcels',
            name: 'Crown Land Parcels',
            geometry_type: 'polygon',
            color: '#2E7D32',
            visible: true,
            popup_fields: ['NAME', 'AREA', 'TYPE']
        }
    ]
};
```

## Customization

### Styling

Edit the `<style>` section in `index.html` to customize:
- Info panel appearance
- Legend styling
- Popup formatting
- Map controls position

### Map Style

Change the base map by editing the `style` parameter in `index.html`:

```javascript
const map = new mapboxgl.Map({
    container: 'map',
    style: 'mapbox://styles/mapbox/satellite-v9', // or outdoors-v12, streets-v12, etc.
    center: CONFIG.DEFAULT_CENTER,
    zoom: CONFIG.DEFAULT_ZOOM
});
```

Available styles:
- `mapbox://styles/mapbox/streets-v12`
- `mapbox://styles/mapbox/outdoors-v12`
- `mapbox://styles/mapbox/light-v11`
- `mapbox://styles/mapbox/dark-v11`
- `mapbox://styles/mapbox/satellite-v9`
- `mapbox://styles/mapbox/satellite-streets-v12`

### Adding Features

The viewer supports:
- Click features for detailed popups
- Toggle layers on/off
- Navigation controls (zoom, rotate)
- Scale indicator

To add more interactivity, see the Mapbox GL JS documentation:
https://docs.mapbox.com/mapbox-gl-js/guides/

## Deployment

### GitHub Pages

1. Push the `web` folder to your repository
2. Enable GitHub Pages in repository settings
3. Set source to the branch containing the web folder
4. Access at: `https://yourusername.github.io/crown-sync/web/`

### Netlify

1. Create a new site on Netlify
2. Point to your repository
3. Set publish directory to `web`
4. Deploy

### Custom Domain

1. Add your domain in Mapbox account settings
2. Update CORS settings if needed
3. Configure your DNS to point to your hosting

## Troubleshooting

### Map not loading
- Check browser console for errors
- Verify Mapbox access token is correct
- Ensure token is public (starts with `pk.`)

### Layers not appearing
- Verify tileset names match uploaded tilesets
- Check that tilesets finished processing in Mapbox
- Confirm username in config matches Mapbox account

### Popups showing wrong data
- Check `popup_fields` array matches your data
- Verify field names are correct (case-sensitive)

## Auto-Refresh

To automatically refresh data, uncomment the auto-refresh line in `index.html`:

```javascript
// Auto-refresh every hour
setInterval(refreshData, 60 * 60 * 1000);
```

Note: This refreshes the page, not the data. Data updates when you run the sync script.
