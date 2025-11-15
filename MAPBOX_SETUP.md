# Mapbox Integration Setup Guide

Complete guide to setting up Mapbox integration for Crown Land data visualization.

## Prerequisites

1. **Mapbox Account**
   - Sign up at https://account.mapbox.com/
   - Free tier includes:
     - 50,000 map loads per month
     - 50 GB tileset storage
     - Sufficient for most use cases

2. **Python Environment**
   ```bash
   pip install -r requirements.txt
   ```

## Step 1: Get Mapbox Tokens

You need TWO types of tokens:

### Secret Token (for uploads)
1. Go to https://account.mapbox.com/access-tokens/
2. Click "Create a token"
3. Name: "Crown Land Sync"
4. Scopes needed:
   - ☑ `uploads:write`
   - ☑ `uploads:read`
   - ☑ `uploads:list`
5. Click "Create token"
6. **Copy the token** (starts with `sk.`) - you won't see it again!

### Public Token (for web maps)
1. Use the default public token from your account
2. Or create a new one with:
   - ☑ `styles:read`
   - ☑ `fonts:read`
3. This token (starts with `pk.`) can be shared publicly

## Step 2: Configure Data Sync

1. **Create configuration file:**
   ```bash
   cp config.example.json config.json
   ```

2. **Edit config.json:**
   ```json
   {
     "mapbox_access_token": "sk.YOUR_SECRET_TOKEN",
     "layers": [
       {
         "service_name": "ServiceName/MapServer",
         "layer_id": 0,
         "tileset_name": "crown_land_parcels",
         "where": "1=1",
         "description": "All crown land parcels"
       }
     ]
   }
   ```

3. **Find Crown Land service names:**
   ```bash
   python -m __main__ list-services
   ```

4. **Test the sync:**
   ```bash
   export MAPBOX_ACCESS_TOKEN="sk.YOUR_SECRET_TOKEN"
   python sync_to_mapbox.py --config config.json
   ```

This will:
- Download data from Crown Land Atlas
- Convert to GeoJSON
- Upload to Mapbox as a tileset
- Wait for processing to complete

## Step 3: Set Up Web Viewer

1. **Configure the viewer:**
   ```bash
   cd web
   cp config.example.js config.js
   ```

2. **Edit config.js:**
   ```javascript
   const CONFIG = {
       MAPBOX_ACCESS_TOKEN: 'pk.YOUR_PUBLIC_TOKEN',
       MAPBOX_USERNAME: 'your-username',
       DEFAULT_CENTER: [-79.38, 43.65], // Toronto
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

3. **Test the viewer:**
   ```bash
   python3 -m http.server 8000
   # Open http://localhost:8000
   ```

## Step 4: Set Up Automation

Choose your preferred method:

### Option A: Cron (Linux/Mac)

```bash
cd automation
chmod +x setup_cron.sh
./setup_cron.sh
```

### Option B: GitHub Actions

1. **Copy workflow file:**
   ```bash
   mkdir -p .github/workflows
   cp automation/github_actions.yml .github/workflows/sync-crown-land.yml
   ```

2. **Add secret to GitHub:**
   - Repository Settings > Secrets and variables > Actions
   - New repository secret:
     - Name: `MAPBOX_ACCESS_TOKEN`
     - Value: `sk.YOUR_SECRET_TOKEN`

3. **Commit and push:**
   ```bash
   git add .github/workflows/sync-crown-land.yml config.json
   git commit -m "Add automated Mapbox sync"
   git push
   ```

### Option C: systemd (Linux servers)

See [automation/README.md](automation/README.md) for systemd setup.

## Step 5: Deploy Web Viewer

### GitHub Pages (Free)

1. **Enable GitHub Pages:**
   - Settings > Pages
   - Source: Deploy from a branch
   - Branch: main, folder: /web

2. **Access your map:**
   ```
   https://your-username.github.io/crown-sync/web/
   ```

### Netlify (Free)

1. **Connect repository to Netlify**
2. **Configure:**
   - Build command: (leave empty)
   - Publish directory: `web`
3. **Deploy**

### Custom Server

```bash
# Apache
<VirtualHost *:80>
    ServerName crown.example.com
    DocumentRoot /path/to/crown-sync/web
</VirtualHost>

# Nginx
server {
    listen 80;
    server_name crown.example.com;
    root /path/to/crown-sync/web;
    index index.html;
}
```

## Verification

### 1. Check Tileset Upload

Visit: https://studio.mapbox.com/tilesets/

You should see your tileset listed (e.g., `your-username.crown_land_parcels`)

### 2. Test in Mapbox Studio

1. Go to https://studio.mapbox.com/
2. Create new style
3. Add layer > Source: Your tileset
4. Style and preview

### 3. Verify Web Map

1. Open your web viewer
2. Check browser console for errors (F12)
3. Verify layers appear
4. Test clicking features for popups
5. Toggle layers on/off

## Troubleshooting

### Upload Fails

**Error: "Invalid token"**
- Verify token starts with `sk.`
- Check token has upload permissions
- Ensure token hasn't expired

**Error: "File too large"**
- GeoJSON > 300MB needs to be split
- Use `--max-records` to limit dataset size
- Filter data with `--where` clause

**Upload stuck "Processing"**
- Wait up to 30 minutes for large datasets
- Check status: https://studio.mapbox.com/tilesets/

### Map Not Loading

**Blank map:**
- Check browser console (F12)
- Verify public token in config.js
- Ensure token starts with `pk.`

**Layers missing:**
- Verify tileset names match config
- Check tileset finished processing
- Confirm username is correct

**Wrong location:**
- Adjust `DEFAULT_CENTER` in config.js
- Use [lng, lat] format (not lat, lng!)

### Automation Not Running

**Cron:**
```bash
# Check if cron job exists
crontab -l

# Test script manually
cd automation
./sync_cron.sh

# Check logs
tail -f ../logs/crown-sync.log
```

**GitHub Actions:**
- Actions tab > View workflow runs
- Check for error messages
- Verify secret is set correctly

## Best Practices

### Security

1. **Never commit tokens to git:**
   ```bash
   # Add to .gitignore
   echo "config.json" >> .gitignore
   echo "web/config.js" >> .gitignore
   ```

2. **Use environment variables:**
   ```bash
   export MAPBOX_ACCESS_TOKEN="sk...."
   ```

3. **Separate tokens:**
   - Development: One token
   - Production: Different token
   - Can revoke individually if compromised

### Performance

1. **Optimize data size:**
   - Use `where` clauses to filter
   - Limit to necessary fields
   - Simplify geometry if possible

2. **Update frequency:**
   - Crown Land data doesn't change daily
   - Weekly or monthly updates often sufficient
   - Saves API quota and processing time

3. **Caching:**
   - Tilesets are cached by Mapbox
   - Updates take time to propagate
   - Consider cache-busting for critical updates

### Monitoring

1. **Set up notifications:**
   - Email on sync failure
   - Slack webhook integration
   - Check logs regularly

2. **Monitor quotas:**
   - Mapbox dashboard shows usage
   - Track map loads
   - Monitor tileset storage

3. **Log retention:**
   ```bash
   # Keep last 30 days
   find logs -name "*.log" -mtime +30 -delete
   ```

## Cost Estimation

### Free Tier Limits

- Map loads: 50,000/month
- Tileset storage: 50 GB
- Uploads: Unlimited

### Typical Usage

- **Small site** (<1000 visitors/month): Free tier sufficient
- **Medium site** (1000-10,000 visitors): $5-20/month
- **Large site** (10,000+ visitors): $50+/month

### Optimization Tips

1. **Use vector tiles** (already done) - more efficient than raster
2. **Lazy load** map viewer
3. **Cache tiles** in browser
4. **Consider self-hosting** tiles for very high traffic

## Next Steps

1. **Customize styling** in Mapbox Studio
2. **Add analysis tools** to web viewer
3. **Integrate search** functionality
4. **Add data download** from web interface
5. **Create mobile app** using Mapbox SDKs

## Resources

- Mapbox Documentation: https://docs.mapbox.com/
- Mapbox GL JS Examples: https://docs.mapbox.com/mapbox-gl-js/example/
- Mapbox Studio: https://studio.mapbox.com/
- Support: https://support.mapbox.com/

## Support

If you encounter issues:

1. Check the [troubleshooting section](#troubleshooting)
2. Review Mapbox documentation
3. Check browser console for errors
4. Review sync logs
5. Create an issue in this repository
