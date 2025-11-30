"""
Constants for HTTP client implementations.

This module contains constants used by HTTP client classes for API communication,
authentication, and error handling.
"""

from ...constants import (
    DEFAULT_TIMEOUT,
    HTTP_RETRY_COUNT,
    RIOT_REPLAY_API_HOST,
    RIOT_REPLAY_API_PORT,
    RIOT_REPLAY_BASE_URL,
    AUTHORIZATION_HEADER,
    BASIC_AUTH_PREFIX,
)

# SSL verification settings
VERIFY_SSL_DEFAULT = False  # Riot APIs use self-signed certificates

# HTTP client settings
DEFAULT_CONNECT_TIMEOUT = DEFAULT_TIMEOUT
DEFAULT_READ_TIMEOUT = DEFAULT_TIMEOUT
DEFAULT_TOTAL_TIMEOUT = DEFAULT_TIMEOUT

# HTTP status codes
HTTP_OK = 200
HTTP_NOT_FOUND = 404
HTTP_INTERNAL_SERVER_ERROR = 500
HTTP_BAD_REQUEST = 400
HTTP_UNAUTHORIZED = 401
HTTP_FORBIDDEN = 403

# Retry settings
RETRY_BACKOFF_FACTOR = 1.0
RETRY_STATUS_FORCELIST = [500, 502, 503, 504]
RETRY_METHOD_WHITELIST = ["GET", "POST", "PUT", "DELETE"]

# Lockfile format constants
LOCKFILE_PARTS_COUNT = 5
LOCKFILE_PROCESS_INDEX = 0
LOCKFILE_PID_INDEX = 1
LOCKFILE_PORT_INDEX = 2
LOCKFILE_PASSWORD_INDEX = 3
LOCKFILE_PROTOCOL_INDEX = 4

# Riot API credential format
RIOT_AUTH_USERNAME = "riot"

# HTTP headers
CONTENT_TYPE_HEADER = "Content-Type"
ACCEPT_HEADER = "Accept"
USER_AGENT_HEADER = "User-Agent"

# Content types
CONTENT_TYPE_JSON = "application/json"
CONTENT_TYPE_FORM = "application/x-www-form-urlencoded"

# LCU API base URL pattern
LCU_BASE_URL_PATTERN = "https://{host}:{port}"

# Request/Response limits
MAX_RESPONSE_SIZE = 10 * 1024 * 1024  # 10MB
MAX_RETRY_ATTEMPTS = HTTP_RETRY_COUNT
RETRY_DELAY_BASE = 1.0  # seconds