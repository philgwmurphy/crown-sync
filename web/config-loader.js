/**
 * Configuration loader for Vercel and local environments
 *
 * Supports:
 * - Vercel environment variables
 * - Local config.js file
 * - URL parameters for testing
 */

// Default configuration
const DEFAULT_CONFIG = {
    MAPBOX_ACCESS_TOKEN: '',
    MAPBOX_USERNAME: '',
    DEFAULT_CENTER: [-84.5, 49.5], // Ontario
    DEFAULT_ZOOM: 5,
    LAYERS: []
};

/**
 * Load configuration from various sources
 */
function loadConfig() {
    let config = { ...DEFAULT_CONFIG };

    // Try to load from config.js (local development)
    if (typeof CONFIG !== 'undefined') {
        config = { ...config, ...CONFIG };
    }

    // Override with environment variables (Vercel)
    if (typeof process !== 'undefined' && process.env) {
        if (process.env.MAPBOX_PUBLIC_TOKEN) {
            config.MAPBOX_ACCESS_TOKEN = process.env.MAPBOX_PUBLIC_TOKEN;
        }
        if (process.env.MAPBOX_USERNAME) {
            config.MAPBOX_USERNAME = process.env.MAPBOX_USERNAME;
        }
    }

    // Override with URL parameters (for testing)
    const urlParams = new URLSearchParams(window.location.search);
    if (urlParams.has('token')) {
        config.MAPBOX_ACCESS_TOKEN = urlParams.get('token');
    }
    if (urlParams.has('username')) {
        config.MAPBOX_USERNAME = urlParams.get('username');
    }

    // Validate configuration
    if (!config.MAPBOX_ACCESS_TOKEN) {
        console.error('Mapbox access token not configured!');
        console.log('Set MAPBOX_PUBLIC_TOKEN environment variable or create config.js');
    }

    if (!config.MAPBOX_USERNAME) {
        console.warn('Mapbox username not configured');
    }

    return config;
}

// Load configuration immediately
const APP_CONFIG = loadConfig();

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = APP_CONFIG;
}
