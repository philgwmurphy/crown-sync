# Automation Scripts

Automate Crown Land data synchronization to Mapbox using various methods.

## Methods

### 1. Cron Job (Linux/Mac)

**Best for:** Running on your own server or computer

**Setup:**

```bash
cd automation
chmod +x setup_cron.sh
./setup_cron.sh
```

This will guide you through setting up a cron job that runs automatically.

**Manual Setup:**

```bash
# Edit crontab
crontab -e

# Add one of these lines:

# Daily at 2 AM
0 2 * * * /path/to/crown-sync/automation/sync_cron.sh >> /var/log/crown-sync.log 2>&1

# Every 6 hours
0 */6 * * * /path/to/crown-sync/automation/sync_cron.sh >> /var/log/crown-sync.log 2>&1

# Weekly on Sunday at 2 AM
0 2 * * 0 /path/to/crown-sync/automation/sync_cron.sh >> /var/log/crown-sync.log 2>&1
```

**View logs:**

```bash
tail -f logs/crown-sync.log
```

### 2. GitHub Actions (Cloud)

**Best for:** No server required, runs in the cloud

**Setup:**

1. Create `.github/workflows/` directory in your repository:
   ```bash
   mkdir -p .github/workflows
   ```

2. Copy the workflow file:
   ```bash
   cp automation/github_actions.yml .github/workflows/sync-crown-land.yml
   ```

3. Add your Mapbox token as a GitHub secret:
   - Go to repository Settings > Secrets and variables > Actions
   - Click "New repository secret"
   - Name: `MAPBOX_ACCESS_TOKEN`
   - Value: Your Mapbox access token (starts with `sk.`)

4. Create `config.json` in the repository root with your layer configurations

5. Commit and push:
   ```bash
   git add .github/workflows/sync-crown-land.yml config.json
   git commit -m "Add automated sync workflow"
   git push
   ```

6. The workflow will run:
   - Daily at 2 AM UTC (adjust schedule in the YAML file)
   - When manually triggered from Actions tab
   - Optionally on every push to main

**Monitor:**
- Go to Actions tab in your repository
- View workflow runs and logs

### 3. Windows Task Scheduler

**Best for:** Windows servers or computers

**Setup:**

1. Create a batch file `sync_cron.bat`:
   ```batch
   @echo off
   cd /d "%~dp0\.."
   python sync_to_mapbox.py --config config.json >> logs\sync.log 2>&1
   ```

2. Open Task Scheduler
3. Create New Task:
   - Name: Crown Land Sync
   - Trigger: Daily at 2:00 AM
   - Action: Start a program
   - Program: `C:\path\to\sync_cron.bat`

### 4. systemd Timer (Linux)

**Best for:** Linux servers with systemd

**Create service file** (`/etc/systemd/system/crown-sync.service`):

```ini
[Unit]
Description=Crown Land Data Sync
After=network.target

[Service]
Type=oneshot
User=yourusername
WorkingDirectory=/path/to/crown-sync
ExecStart=/usr/bin/python3 /path/to/crown-sync/sync_to_mapbox.py --config /path/to/crown-sync/config.json
StandardOutput=append:/var/log/crown-sync.log
StandardError=append:/var/log/crown-sync.log

[Install]
WantedBy=multi-user.target
```

**Create timer file** (`/etc/systemd/system/crown-sync.timer`):

```ini
[Unit]
Description=Crown Land Data Sync Timer

[Timer]
OnCalendar=daily
OnCalendar=02:00
Persistent=true

[Install]
WantedBy=timers.target
```

**Enable and start:**

```bash
sudo systemctl enable crown-sync.timer
sudo systemctl start crown-sync.timer

# Check status
sudo systemctl status crown-sync.timer

# View logs
journalctl -u crown-sync.service
```

## Configuration

All methods use `config.json` for layer configuration. Example:

```json
{
  "mapbox_access_token": "sk.YOUR_SECRET_TOKEN",
  "layers": [
    {
      "service_name": "CrownLand/MapServer",
      "layer_id": 0,
      "tileset_name": "crown_land_parcels",
      "where": "1=1"
    }
  ]
}
```

**Important:** Use a **secret token** (starts with `sk.`) for automated syncing, not a public token.

## Monitoring

### Check if sync is running:

```bash
# Cron
ps aux | grep sync_to_mapbox

# systemd
systemctl status crown-sync.service

# GitHub Actions
# Check the Actions tab in your repository
```

### View recent logs:

```bash
# Cron
tail -f logs/crown-sync.log

# systemd
journalctl -u crown-sync.service -f

# GitHub Actions
# Download artifacts from the Actions tab
```

### Test manually:

```bash
python sync_to_mapbox.py --config config.json
```

## Troubleshooting

### Sync not running

**Cron:**
- Check cron is running: `systemctl status cron`
- Verify crontab entry: `crontab -l`
- Check script permissions: `ls -l automation/sync_cron.sh`

**GitHub Actions:**
- Check workflow file syntax
- Verify secret is set correctly
- Check Actions tab for error messages

**systemd:**
- Check timer status: `systemctl status crown-sync.timer`
- View service logs: `journalctl -u crown-sync.service`

### Authentication errors

- Verify Mapbox token is correct and has upload permissions
- For GitHub Actions, ensure secret name matches exactly
- Check token hasn't expired

### Data not updating

- Check logs for errors
- Verify Crown Land API is accessible
- Ensure enough disk space for temporary files
- Check Mapbox upload quotas

## Best Practices

1. **Use different tokens for development and production**
2. **Monitor logs regularly** to catch failures
3. **Set up notifications** for failed syncs (email, Slack, etc.)
4. **Test manually first** before enabling automation
5. **Backup your config files**
6. **Rotate logs** to prevent disk space issues
7. **Document your schedule** so team members know when updates occur

## Notification Setup

### Email on failure (cron):

Add to `sync_cron.sh`:

```bash
if ! python3 sync_to_mapbox.py --config "$CONFIG_FILE" >> "$LOG_FILE" 2>&1; then
    echo "Crown Land sync failed" | mail -s "Sync Failed" you@example.com
fi
```

### Slack notification:

```bash
if ! python3 sync_to_mapbox.py --config "$CONFIG_FILE" >> "$LOG_FILE" 2>&1; then
    curl -X POST -H 'Content-type: application/json' \
        --data '{"text":"Crown Land sync failed!"}' \
        YOUR_SLACK_WEBHOOK_URL
fi
```

## Security Notes

- **Never commit tokens to git** - use environment variables or secrets
- **Use secret tokens** (sk.) for automation, public tokens (pk.) only for web maps
- **Restrict token permissions** to only what's needed (uploads, tilesets)
- **Rotate tokens periodically**
- **Monitor token usage** in Mapbox dashboard
