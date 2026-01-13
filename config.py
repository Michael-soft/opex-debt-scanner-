# Configuration constants for OpsEx Debt Scanner

# ML Configuration
ML_RANDOM_STATE = 42
DEFAULT_CONTAMINATION = 0.05
MIN_CONTAMINATION = 0.01
MAX_CONTAMINATION = 0.15

# Data Generation
SYNTHETIC_ENDPOINTS = [
    '/api/v1/auth/login',
    '/api/v1/transactions/process',
    '/api/v1/reports/generate',
    '/api/v1/user/profile',
    '/api/v1/search/query'
]

ENDPOINT_DISTRIBUTION = [0.3, 0.2, 0.1, 0.2, 0.2]

# Latency Ranges (milliseconds)
HEALTHY_LATENCY_MEAN = 150
HEALTHY_LATENCY_STD = 50
DEBT_LATENCY_MEAN = 1500
DEBT_LATENCY_STD = 300
MIN_LATENCY = 10

# Percentiles for SLA Tracking
PERCENTILES = {
    'p50': 0.50,
    'p75': 0.75,
    'p95': 0.95,
    'p99': 0.99
}

# Alert Thresholds
DEFAULT_WASTED_HOURS_THRESHOLD = 5.0
DEFAULT_ERROR_RATE_THRESHOLD = 1.0

# Financial Metrics
DEFAULT_HOURLY_RATE = 60
MIN_HOURLY_RATE = 10

# UI Configuration
PAGE_TITLE = "OpsEx Debt Scanner"
PAGE_ICON = "🛡️"
LAYOUT = "wide"
SIDEBAR_STATE = "expanded"

# Colors
COLOR_HEALTHY = "#09ab3b"
COLOR_DEBT = "#ff4b4b"
COLOR_BASELINE = "blue"
COLOR_BACKGROUND = "#f0f2f6"

# Chart Configuration
CHART_HEIGHT = 400
TABLE_HEIGHT = 300
