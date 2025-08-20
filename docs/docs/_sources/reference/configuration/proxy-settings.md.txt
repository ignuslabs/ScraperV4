# Proxy Settings Reference

This document provides complete configuration reference for proxy settings in ScraperV4.

## Proxy Configuration Overview

ScraperV4 supports multiple proxy types and rotation strategies to enhance scraping reliability and bypass rate limiting. Proxies can be configured globally or per-template.

## Proxy Types Supported

### HTTP Proxies
Standard HTTP proxies for web scraping:

```json
{
  "proxy_config": {
    "type": "http",
    "host": "proxy.example.com",
    "port": 8080,
    "username": "proxy_user",
    "password": "proxy_pass",
    "protocol": "http"
  }
}
```

### HTTPS Proxies
Secure HTTPS proxies for encrypted connections:

```json
{
  "proxy_config": {
    "type": "https",
    "host": "secure-proxy.example.com",
    "port": 8443,
    "username": "proxy_user",
    "password": "proxy_pass",
    "protocol": "https",
    "verify_ssl": true
  }
}
```

### SOCKS4 Proxies
SOCKS4 protocol proxies:

```json
{
  "proxy_config": {
    "type": "socks4",
    "host": "socks4.example.com",
    "port": 1080,
    "username": "socks_user"
  }
}
```

### SOCKS5 Proxies
SOCKS5 protocol proxies with authentication:

```json
{
  "proxy_config": {
    "type": "socks5",
    "host": "socks5.example.com",
    "port": 1080,
    "username": "socks_user",
    "password": "socks_pass",
    "dns_resolution": "remote"
  }
}
```

## Environment Variables

### Global Proxy Settings

**PROXY_ENABLED** *(optional)*
- **Default:** `False`
- **Type:** Boolean
- **Description:** Enable global proxy usage
- **Example:** `PROXY_ENABLED=True`

**PROXY_TYPE** *(optional)*
- **Default:** `http`
- **Options:** `http`, `https`, `socks4`, `socks5`
- **Description:** Default proxy type
- **Example:** `PROXY_TYPE=socks5`

**PROXY_HOST** *(optional)*
- **Type:** String
- **Description:** Proxy server hostname or IP address
- **Example:** `PROXY_HOST=proxy.example.com`

**PROXY_PORT** *(optional)*
- **Type:** Integer
- **Range:** 1-65535
- **Description:** Proxy server port
- **Example:** `PROXY_PORT=8080`

**PROXY_USERNAME** *(optional)*
- **Type:** String
- **Description:** Proxy authentication username
- **Example:** `PROXY_USERNAME=my_proxy_user`

**PROXY_PASSWORD** *(optional)*
- **Type:** String
- **Description:** Proxy authentication password
- **Example:** `PROXY_PASSWORD=my_proxy_password`

### Proxy Rotation Settings

**PROXY_ROTATION_ENABLED** *(optional)*
- **Default:** `False`
- **Type:** Boolean
- **Description:** Enable automatic proxy rotation
- **Example:** `PROXY_ROTATION_ENABLED=True`

**PROXY_LIST_FILE** *(optional)*
- **Type:** String
- **Description:** Path to file containing proxy list
- **Example:** `PROXY_LIST_FILE=/etc/scraperv4/proxies.txt`

**PROXY_ROTATION_STRATEGY** *(optional)*
- **Default:** `round_robin`
- **Options:** `round_robin`, `random`, `health_based`, `geographic`
- **Description:** Proxy selection strategy
- **Example:** `PROXY_ROTATION_STRATEGY=health_based`

**PROXY_ROTATION_INTERVAL** *(optional)*
- **Default:** `10`
- **Type:** Integer
- **Unit:** Requests
- **Description:** Number of requests before proxy rotation
- **Example:** `PROXY_ROTATION_INTERVAL=5`

**PROXY_HEALTH_CHECK_ENABLED** *(optional)*
- **Default:** `True`
- **Type:** Boolean
- **Description:** Enable proxy health monitoring
- **Example:** `PROXY_HEALTH_CHECK_ENABLED=False`

**PROXY_HEALTH_CHECK_INTERVAL** *(optional)*
- **Default:** `300`
- **Type:** Integer
- **Unit:** Seconds
- **Description:** Proxy health check frequency
- **Example:** `PROXY_HEALTH_CHECK_INTERVAL=600`

**PROXY_TIMEOUT** *(optional)*
- **Default:** `30`
- **Type:** Integer
- **Unit:** Seconds
- **Description:** Proxy connection timeout
- **Example:** `PROXY_TIMEOUT=60`

**PROXY_RETRY_ATTEMPTS** *(optional)*
- **Default:** `3`
- **Type:** Integer
- **Description:** Retry attempts for failed proxy connections
- **Example:** `PROXY_RETRY_ATTEMPTS=5`

## Proxy List Configuration

### Proxy List File Format

Create a text file with one proxy per line in the following formats:

#### Basic Format
```
proxy1.example.com:8080
proxy2.example.com:8080
proxy3.example.com:8080
```

#### With Authentication
```
username:password@proxy1.example.com:8080
username:password@proxy2.example.com:8080
username:password@proxy3.example.com:8080
```

#### Full URL Format
```
http://proxy1.example.com:8080
https://username:password@proxy2.example.com:8443
socks5://username:password@proxy3.example.com:1080
socks4://proxy4.example.com:1080
```

#### JSON Format
```json
[
  {
    "type": "http",
    "host": "proxy1.example.com",
    "port": 8080,
    "username": "user1",
    "password": "pass1",
    "location": "US",
    "speed": "fast",
    "uptime": 99.5
  },
  {
    "type": "socks5",
    "host": "proxy2.example.com",
    "port": 1080,
    "username": "user2",
    "password": "pass2",
    "location": "EU",
    "speed": "medium",
    "uptime": 98.2
  }
]
```

### Proxy Metadata

Enhanced proxy configurations can include metadata for intelligent routing:

```json
{
  "proxies": [
    {
      "id": "proxy_001",
      "type": "http",
      "host": "us-proxy.example.com",
      "port": 8080,
      "username": "user",
      "password": "pass",
      "metadata": {
        "location": {
          "country": "US",
          "region": "California",
          "city": "San Francisco"
        },
        "performance": {
          "speed": "fast",
          "uptime": 99.8,
          "latency": 45
        },
        "limits": {
          "requests_per_minute": 100,
          "concurrent_connections": 10,
          "bandwidth": "100Mbps"
        },
        "features": {
          "supports_https": true,
          "residential": false,
          "datacenter": true
        }
      }
    }
  ]
}
```

## Template-Level Proxy Configuration

### Per-Template Proxy Settings

Templates can specify their own proxy requirements:

```json
{
  "name": "geo_specific_scraper",
  "description": "Scraper requiring US-based proxies",
  
  "proxy_config": {
    "enabled": true,
    "required": true,
    "type": "http",
    "rotation": {
      "enabled": true,
      "strategy": "geographic",
      "interval": 5
    },
    "requirements": {
      "location": "US",
      "speed": "fast",
      "residential": true
    },
    "fallback": {
      "enabled": true,
      "direct_connection": false,
      "alternative_proxies": ["EU", "CA"]
    }
  },
  
  "fetcher_config": {
    "type": "stealth",
    "proxy_integration": true
  }
}
```

### Proxy Requirements

Templates can specify proxy requirements for optimal performance:

```json
{
  "proxy_requirements": {
    "mandatory": true,
    "type": ["http", "https"],
    "location": {
      "country": "US",
      "exclude": ["CN", "RU"]
    },
    "performance": {
      "min_speed": "medium",
      "min_uptime": 95.0,
      "max_latency": 100
    },
    "features": {
      "residential": true,
      "ssl_support": true,
      "concurrent_sessions": 5
    }
  }
}
```

## Rotation Strategies

### Round Robin
Cycles through proxies in order:

```json
{
  "rotation_strategy": "round_robin",
  "rotation_config": {
    "interval": 10,
    "reset_on_failure": true
  }
}
```

### Random Selection
Randomly selects from available proxies:

```json
{
  "rotation_strategy": "random",
  "rotation_config": {
    "interval": 5,
    "weighted": true,
    "weights": {
      "uptime": 0.4,
      "speed": 0.3,
      "location": 0.3
    }
  }
}
```

### Health-Based Selection
Prioritizes proxies based on health metrics:

```json
{
  "rotation_strategy": "health_based",
  "rotation_config": {
    "health_threshold": 95.0,
    "failure_penalty": 10,
    "recovery_time": 300,
    "metrics": ["uptime", "response_time", "success_rate"]
  }
}
```

### Geographic Routing
Routes requests based on target website location:

```json
{
  "rotation_strategy": "geographic",
  "rotation_config": {
    "target_matching": true,
    "fallback_regions": ["US", "EU", "ANY"],
    "latency_optimization": true
  }
}
```

## Proxy Health Monitoring

### Health Check Configuration

```json
{
  "health_monitoring": {
    "enabled": true,
    "check_interval": 300,
    "check_timeout": 10,
    "check_url": "http://httpbin.org/ip",
    "expected_response": {
      "status_code": 200,
      "contains": "origin"
    },
    "failure_threshold": 3,
    "recovery_threshold": 2,
    "quarantine_duration": 600
  }
}
```

### Health Metrics

ScraperV4 tracks various proxy health metrics:

- **Uptime**: Percentage of successful health checks
- **Response Time**: Average response time for health checks
- **Success Rate**: Percentage of successful scraping requests
- **Error Rate**: Percentage of failed requests
- **Bandwidth**: Data transfer speed
- **Concurrent Connections**: Number of active connections

### Automatic Proxy Management

```json
{
  "automatic_management": {
    "enabled": true,
    "actions": {
      "quarantine_failed": true,
      "rotate_on_failure": true,
      "prefer_healthy": true,
      "load_balance": true
    },
    "thresholds": {
      "failure_rate": 10.0,
      "response_time": 5000,
      "quarantine_failures": 5
    }
  }
}
```

## Fetcher Integration

### HTTP/HTTPS Fetchers

Basic and async fetchers support proxy configuration:

```json
{
  "fetcher_config": {
    "type": "async",
    "proxy": {
      "enabled": true,
      "type": "http",
      "host": "proxy.example.com",
      "port": 8080,
      "auth": {
        "username": "proxy_user",
        "password": "proxy_pass"
      }
    }
  }
}
```

### Stealth Fetcher

Stealth fetcher with proxy integration:

```json
{
  "fetcher_config": {
    "type": "stealth",
    "proxy": {
      "enabled": true,
      "type": "socks5",
      "host": "socks-proxy.example.com",
      "port": 1080,
      "auth": {
        "username": "socks_user",
        "password": "socks_pass"
      }
    },
    "stealth_options": {
      "proxy_chain": true,
      "dns_over_proxy": true,
      "webrtc_leak_prevention": true
    }
  }
}
```

### Playwright Fetcher

Playwright with proxy support:

```json
{
  "fetcher_config": {
    "type": "playwright",
    "proxy": {
      "server": "http://proxy.example.com:8080",
      "username": "proxy_user",
      "password": "proxy_pass",
      "bypass": "localhost,127.0.0.1,*.local"
    },
    "browser_options": {
      "headless": true,
      "ignore_https_errors": true
    }
  }
}
```

## Security Considerations

### Proxy Authentication Security

```json
{
  "security_config": {
    "encrypt_credentials": true,
    "credential_storage": "environment",
    "rotation_on_exposure": true,
    "ip_whitelist": ["192.168.1.0/24"],
    "ssl_verification": true,
    "certificate_pinning": false
  }
}
```

### IP Leak Prevention

```json
{
  "leak_prevention": {
    "dns_leak_protection": true,
    "webrtc_leak_protection": true,
    "timezone_spoofing": true,
    "geolocation_spoofing": true,
    "ipv6_blocking": true
  }
}
```

## Error Handling

### Proxy Error Types

ScraperV4 handles various proxy-related errors:

- **CONNECTION_FAILED**: Cannot connect to proxy server
- **AUTHENTICATION_FAILED**: Invalid proxy credentials
- **TIMEOUT_ERROR**: Proxy connection timeout
- **PROTOCOL_ERROR**: Proxy protocol mismatch
- **RATE_LIMITED**: Proxy rate limit exceeded
- **BANNED_IP**: Target website blocked proxy IP
- **DNS_RESOLUTION_FAILED**: Cannot resolve proxy hostname

### Error Response Format

```json
{
  "success": false,
  "error": "PROXY_CONNECTION_FAILED",
  "message": "Failed to connect to proxy server",
  "details": {
    "proxy_host": "proxy.example.com",
    "proxy_port": 8080,
    "error_code": "ECONNREFUSED",
    "retry_count": 3,
    "next_proxy": "proxy2.example.com:8080"
  }
}
```

### Automatic Error Recovery

```json
{
  "error_recovery": {
    "enabled": true,
    "max_retries": 3,
    "retry_delay": [1, 5],
    "fallback_strategies": [
      "rotate_proxy",
      "direct_connection",
      "alternative_fetcher"
    ],
    "circuit_breaker": {
      "enabled": true,
      "failure_threshold": 5,
      "recovery_timeout": 300
    }
  }
}
```

## Performance Optimization

### Connection Pooling

```json
{
  "connection_pooling": {
    "enabled": true,
    "pool_size": 10,
    "max_connections_per_proxy": 5,
    "connection_timeout": 30,
    "idle_timeout": 300,
    "keep_alive": true
  }
}
```

### Proxy Caching

```json
{
  "proxy_caching": {
    "enabled": true,
    "cache_responses": true,
    "cache_duration": 3600,
    "cache_size": "100MB",
    "cache_invalidation": "ttl"
  }
}
```

### Load Balancing

```json
{
  "load_balancing": {
    "enabled": true,
    "algorithm": "least_connections",
    "health_check_weight": 0.3,
    "response_time_weight": 0.4,
    "success_rate_weight": 0.3,
    "max_requests_per_proxy": 100
  }
}
```

## Monitoring and Analytics

### Proxy Usage Statistics

ScraperV4 provides detailed proxy usage analytics:

```json
{
  "proxy_analytics": {
    "requests_per_proxy": {
      "proxy1.example.com:8080": 1250,
      "proxy2.example.com:8080": 987
    },
    "success_rates": {
      "proxy1.example.com:8080": 95.2,
      "proxy2.example.com:8080": 93.8
    },
    "average_response_times": {
      "proxy1.example.com:8080": 1.2,
      "proxy2.example.com:8080": 1.8
    },
    "error_counts": {
      "proxy1.example.com:8080": 12,
      "proxy2.example.com:8080": 18
    }
  }
}
```

### Real-time Monitoring

```json
{
  "monitoring": {
    "real_time_stats": true,
    "alert_thresholds": {
      "failure_rate": 15.0,
      "response_time": 3.0,
      "queue_length": 50
    },
    "notification_channels": ["log", "webhook"],
    "dashboard_enabled": true
  }
}
```

## See Also

- [Environment Variables](environment-variables.md) - Global proxy environment variables
- [Stealth Options](stealth-options.md) - Stealth mode proxy integration
- [Fetcher Configuration](../classes/scrapers.md) - Fetcher proxy implementation
- [Error Handling](../error-handling.md) - Proxy error codes and handling