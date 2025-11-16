# Deploying to Vercel

Deploy your Crown Land Atlas map viewer to Vercel for free hosting with a custom domain.

## Prerequisites

1. **Mapbox Account** with:
   - Public access token (starts with `pk.`)
   - At least one tileset uploaded

2. **Vercel Account**
   - Sign up at https://vercel.com (free tier available)

3. **GitHub Repository**
   - Push this project to GitHub

## Quick Deploy

### Option 1: Deploy with Vercel CLI

```bash
# Install Vercel CLI
npm install -g vercel

# Login to Vercel
vercel login

# Deploy
vercel

# Follow the prompts:
# - Set up and deploy? Yes
# - Which scope? Your account
# - Link to existing project? No
# - Project name: crown-land-atlas
# - Directory: ./
# - Override settings? No

# Add environment variables
vercel env add MAPBOX_PUBLIC_TOKEN
# Paste your pk.XXXX token

vercel env add MAPBOX_USERNAME
# Enter your Mapbox username

# Deploy to production
vercel --prod
```

### Option 2: Deploy via Vercel Dashboard

1. **Go to Vercel Dashboard**
   - Visit https://vercel.com/dashboard
   - Click "Add New Project"

2. **Import Repository**
   - Select your GitHub repository
   - Click "Import"

3. **Configure Project**
   - Framework Preset: `Other`
   - Root Directory: `./`
   - Build Command: (leave empty)
   - Output Directory: `web`
   - Install Command: (leave empty)

4. **Add Environment Variables**
   - Click "Environment Variables"
   - Add:
     - `MAPBOX_PUBLIC_TOKEN` = `pk.your_token_here`
     - `MAPBOX_USERNAME` = `your_username`

5. **Deploy**
   - Click "Deploy"
   - Wait for deployment to complete
   - Your site will be live at `https://your-project.vercel.app`

### Option 3: One-Click Deploy

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https%3A%2F%2Fgithub.com%2Fyour-username%2Fcrown-sync&env=MAPBOX_PUBLIC_TOKEN,MAPBOX_USERNAME&project-name=crown-land-atlas)

After clicking:
1. Fork/import the repository
2. Add environment variables
3. Deploy!

## Configuration

### Environment Variables

Set these in Vercel Dashboard → Settings → Environment Variables:

| Variable | Description | Example |
|----------|-------------|---------|
| `MAPBOX_PUBLIC_TOKEN` | Your Mapbox public token | `pk.eyJ1IjoieW...` |
| `MAPBOX_USERNAME` | Your Mapbox username | `your-username` |

**Important:** Use your **public token** (pk.) not secret token (sk.) for the web app.

### Layer Configuration

Since environment variables don't support complex JSON, you have two options:

#### Option A: Use config.js (Recommended for Testing)

1. Create `web/config.js` based on `web/config.example.js`:

```javascript
const CONFIG = {
    MAPBOX_ACCESS_TOKEN: 'pk.your_public_token',
    MAPBOX_USERNAME: 'your-username',
    DEFAULT_CENTER: [-79.3832, 43.6532],
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

2. Deploy with this file in your repository
3. **Note:** Remove sensitive tokens before committing to public repos

#### Option B: Hardcode in index.html (Production)

1. Edit `web/config-loader.js` to include your layers:

```javascript
const DEFAULT_CONFIG = {
    MAPBOX_ACCESS_TOKEN: '',
    MAPBOX_USERNAME: '',
    DEFAULT_CENTER: [-79.3832, 43.6532],
    DEFAULT_ZOOM: 8,
    LAYERS: [
        {
            tileset_name: 'crown_land_parcels',
            name: 'Crown Land Parcels',
            geometry_type: 'polygon',
            color: '#2E7D32',
            visible: true
        }
    ]
};
```

2. Tokens will come from environment variables
3. Layers are defined in code

## Custom Domain

### Add Your Domain

1. **In Vercel Dashboard**
   - Go to Project → Settings → Domains
   - Click "Add Domain"
   - Enter your domain: `crownland.yourdomain.com`

2. **Update DNS**
   - Add CNAME record:
     - Type: `CNAME`
     - Name: `crownland` (or `@` for root domain)
     - Value: `cname.vercel-dns.com`

3. **Wait for DNS Propagation**
   - Usually takes 5-60 minutes
   - Vercel will auto-provision SSL certificate

## Automatic Deployments

Vercel automatically deploys when you push to GitHub:

- **Push to main branch** → Production deployment
- **Push to other branches** → Preview deployment
- **Pull requests** → Preview deployment with unique URL

### Configure Branches

In Vercel Dashboard → Settings → Git:
- Production Branch: `main` (or `master`)
- Enable Preview Deployments: Yes
- Enable Production Deployments: Yes

## Updating Data

When you upload new tilesets to Mapbox:

1. **Tilesets update automatically**
   - Mapbox serves the latest version
   - No redeployment needed

2. **To add new layers:**
   - Update `config.js` or `config-loader.js`
   - Commit and push to GitHub
   - Vercel redeploys automatically

3. **Manual redeploy:**
   - Dashboard → Deployments → Latest → "⋮" → Redeploy

## Monitoring

### Analytics

Vercel provides:
- Page views
- Visitor count
- Performance metrics

Access at: Dashboard → Project → Analytics

### Performance

Check your site speed:
- Vercel Analytics (built-in)
- Google PageSpeed Insights
- GTmetrix

### Error Tracking

View errors in:
- Browser console (F12)
- Vercel → Deployments → Build Logs
- Vercel → Analytics → Errors

## Troubleshooting

### Map Not Loading

**Issue:** Blank map or "Unauthorized" error

**Solutions:**
1. Check environment variables are set correctly
2. Verify public token starts with `pk.`
3. Check browser console for errors
4. Ensure token has correct scopes

### Layers Not Appearing

**Issue:** Map loads but no data layers

**Solutions:**
1. Verify tileset names match exactly
2. Check Mapbox username is correct
3. Ensure tilesets finished processing in Mapbox Studio
4. Check browser console for 404 errors

### Build Fails

**Issue:** Deployment fails to build

**Solutions:**
1. Check build logs in Vercel dashboard
2. Ensure `vercel.json` is valid JSON
3. Verify file structure is correct
4. Check for syntax errors in JavaScript files

### Domain Not Working

**Issue:** Custom domain shows error

**Solutions:**
1. Verify DNS records are correct
2. Wait for DNS propagation (up to 48 hours)
3. Check domain status in Vercel dashboard
4. Ensure domain is not already in use

## Cost

### Vercel Pricing

**Hobby Plan (Free):**
- ✓ Unlimited websites
- ✓ 100GB bandwidth/month
- ✓ 100 deployments/day
- ✓ Automatic HTTPS
- ✓ Preview deployments

**Pro Plan ($20/month):**
- ✓ Everything in Hobby
- ✓ 1TB bandwidth/month
- ✓ Advanced analytics
- ✓ Password protection
- ✓ Team collaboration

**For this project:** Free tier is usually sufficient

### Mapbox Pricing

**Free Tier:**
- ✓ 50,000 map loads/month
- ✓ 50 GB tileset storage

**Pay-as-you-go:**
- $0.50 per 1,000 loads (after free tier)

**For this project:** Free tier covers most personal/small sites

## Performance Optimization

### Enable Caching

Vercel automatically caches static assets. Optimize further:

1. **Add headers in vercel.json:**

```json
{
  "headers": [
    {
      "source": "/(.*)",
      "headers": [
        {
          "key": "Cache-Control",
          "value": "public, max-age=31536000, immutable"
        }
      ]
    }
  ]
}
```

### Optimize Images

If you add images:
- Use WebP format
- Compress before uploading
- Use Vercel Image Optimization

### Minimize JavaScript

Code is already minimal, but you can:
- Enable minification in Vercel
- Remove unused layers from config
- Lazy load map only when needed

## Security

### Best Practices

1. **Never commit secrets**
   - Use environment variables
   - Add `config.js` to `.gitignore`

2. **Use public tokens only**
   - Never use secret tokens (sk.) in frontend
   - Restrict token permissions in Mapbox

3. **Enable HTTPS**
   - Automatic with Vercel
   - Force HTTPS redirects (default)

4. **Set CORS headers**
   - Already configured in `vercel.json`

## Advanced Configuration

### Custom Build Process

If you need to build data files:

1. **Add build script to vercel.json:**

```json
{
  "builds": [
    {
      "src": "build.sh",
      "use": "@vercel/static-build",
      "config": {
        "distDir": "web"
      }
    }
  ]
}
```

2. **Create build.sh:**

```bash
#!/bin/bash
# Download latest data
python3 local_data.py prepare --input data.geojson
# Copy to web directory
cp data.geojson web/
```

### Serverless Functions

Add API endpoints for dynamic features:

1. **Create api/ directory:**

```
project/
└── api/
    └── layers.js
```

2. **Example function (api/layers.js):**

```javascript
module.exports = (req, res) => {
  res.json({
    layers: [
      {
        name: 'Crown Land',
        tileset: 'crown_land_parcels'
      }
    ]
  });
};
```

3. **Access at:** `https://your-site.vercel.app/api/layers`

## Support

### Resources

- Vercel Docs: https://vercel.com/docs
- Mapbox Docs: https://docs.mapbox.com/
- Community: https://github.com/vercel/vercel/discussions

### Getting Help

1. Check Vercel build logs
2. Review browser console
3. Search Vercel documentation
4. Ask in Vercel Discord
5. Create issue in this repository

## Next Steps

After deployment:

1. ✓ **Test your map** - verify layers load correctly
2. ✓ **Add custom domain** - make it professional
3. ✓ **Set up analytics** - track usage
4. ✓ **Monitor performance** - optimize as needed
5. ✓ **Share your map** - distribute the URL!

Your Crown Land Atlas is now live! 🎉
