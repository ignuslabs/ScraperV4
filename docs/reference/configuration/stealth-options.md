# Stealth Options Reference

This document provides complete configuration reference for stealth mode options in ScraperV4, designed to bypass anti-bot protection and appear as a regular browser.

## Stealth Mode Overview

ScraperV4's stealth mode uses advanced techniques to mimic human browsing behavior and avoid detection by anti-bot systems. It includes browser fingerprint randomization, behavioral simulation, and traffic pattern masking.

## Environment Variables

### Global Stealth Settings

**STEALTH_MODE_ENABLED** *(optional)*
- **Default:** `True`
- **Type:** Boolean
- **Description:** Enable global stealth mode
- **Example:** `STEALTH_MODE_ENABLED=False`

**STEALTH_LEVEL** *(optional)*
- **Default:** `medium`
- **Options:** `low`, `medium`, `high`, `maximum`
- **Description:** Overall stealth aggressiveness level
- **Example:** `STEALTH_LEVEL=high`

**HEADLESS_MODE** *(optional)*
- **Default:** `True`
- **Type:** Boolean
- **Description:** Run browsers in headless mode
- **Example:** `HEADLESS_MODE=False`

**HUMANIZE_BEHAVIOR** *(optional)*
- **Default:** `True`
- **Type:** Boolean
- **Description:** Enable human-like behavior simulation
- **Example:** `HUMANIZE_BEHAVIOR=False`

### Browser Fingerprinting

**RANDOMIZE_USER_AGENT** *(optional)*
- **Default:** `True`
- **Type:** Boolean
- **Description:** Randomize User-Agent headers
- **Example:** `RANDOMIZE_USER_AGENT=False`

**SPOOF_CANVAS** *(optional)*
- **Default:** `True`
- **Type:** Boolean
- **Description:** Spoof canvas fingerprinting
- **Example:** `SPOOF_CANVAS=False`

**SPOOF_WEBGL** *(optional)*
- **Default:** `True`
- **Type:** Boolean
- **Description:** Spoof WebGL fingerprinting
- **Example:** `SPOOF_WEBGL=False`

**RANDOMIZE_VIEWPORT** *(optional)*
- **Default:** `True`
- **Type:** Boolean
- **Description:** Randomize browser viewport size
- **Example:** `RANDOMIZE_VIEWPORT=False`

**OS_RANDOMIZATION** *(optional)*
- **Default:** `True`
- **Type:** Boolean
- **Description:** Randomize operating system fingerprints
- **Example:** `OS_RANDOMIZATION=False`

### Network and Privacy

**BLOCK_WEBRTC** *(optional)*
- **Default:** `True`
- **Type:** Boolean
- **Description:** Block WebRTC to prevent IP leaks
- **Example:** `BLOCK_WEBRTC=False`

**DISABLE_WEBGL** *(optional)*
- **Default:** `False`
- **Type:** Boolean
- **Description:** Completely disable WebGL
- **Example:** `DISABLE_WEBGL=True`

**BLOCK_GEOLOCATION** *(optional)*
- **Default:** `True`
- **Type:** Boolean
- **Description:** Block geolocation API
- **Example:** `BLOCK_GEOLOCATION=False`

**SPOOF_TIMEZONE** *(optional)*
- **Default:** `True`
- **Type:** Boolean
- **Description:** Spoof browser timezone
- **Example:** `SPOOF_TIMEZONE=False`

**TARGET_TIMEZONE** *(optional)*
- **Default:** `auto`
- **Description:** Target timezone for spoofing
- **Example:** `TARGET_TIMEZONE=America/New_York`

### Traffic Patterns

**GOOGLE_SEARCH_SIMULATION** *(optional)*
- **Default:** `True`
- **Type:** Boolean
- **Description:** Simulate arriving from Google search
- **Example:** `GOOGLE_SEARCH_SIMULATION=False`

**REFERRER_SPOOFING** *(optional)*
- **Default:** `True`
- **Type:** Boolean
- **Description:** Spoof HTTP referrer headers
- **Example:** `REFERRER_SPOOFING=False`

**RANDOM_DELAYS** *(optional)*
- **Default:** `True`
- **Type:** Boolean
- **Description:** Add random delays between actions
- **Example:** `RANDOM_DELAYS=False`

**MIN_ACTION_DELAY** *(optional)*
- **Default:** `0.5`
- **Type:** Float
- **Unit:** Seconds
- **Description:** Minimum delay between browser actions
- **Example:** `MIN_ACTION_DELAY=1.0`

**MAX_ACTION_DELAY** *(optional)*
- **Default:** `3.0`
- **Type:** Float
- **Unit:** Seconds
- **Description:** Maximum delay between browser actions
- **Example:** `MAX_ACTION_DELAY=5.0`

## Template-Level Stealth Configuration

### Basic Stealth Template Config

```json
{
  "name": "stealth_scraper",
  "description": "High-stealth scraper for protected sites",
  
  "fetcher_config": {
    "type": "stealth",
    "stealth_level": "high",
    "headless": true,
    "humanize": true,
    
    "anti_detection": {
      "block_webrtc": true,
      "spoof_canvas": true,
      "spoof_webgl": true,
      "randomize_fingerprints": true,
      "os_randomization": true
    },
    
    "behavior_simulation": {
      "mouse_movements": true,
      "scroll_behavior": true,
      "typing_patterns": true,
      "reading_patterns": true
    },
    
    "traffic_masking": {
      "google_search": true,
      "referrer_spoofing": true,
      "random_delays": true,
      "session_simulation": true
    }
  }
}
```

### Advanced Stealth Configuration

```json
{
  "fetcher_config": {
    "type": "stealth",
    "stealth_options": {
      "detection_evasion": {
        "webdriver_detection": {
          "enabled": true,
          "level": "aggressive",
          "patch_selenium_flags": true,
          "remove_automation_flags": true,
          "spoof_chrome_runtime": true
        },
        "bot_detection": {
          "enabled": true,
          "challenge_solving": true,
          "captcha_detection": true,
          "behavioral_analysis_evasion": true
        },
        "fingerprint_resistance": {
          "canvas_randomization": true,
          "webgl_randomization": true,
          "audio_fingerprint_spoofing": true,
          "font_fingerprint_spoofing": true,
          "screen_resolution_spoofing": true
        }
      },
      
      "browser_simulation": {
        "user_agent": {
          "randomize": true,
          "prefer_recent": true,
          "match_platform": true,
          "whitelist": ["Chrome", "Firefox", "Safari"]
        },
        "viewport": {
          "randomize": true,
          "common_resolutions": true,
          "mobile_simulation": false
        },
        "plugins": {
          "simulate_common": true,
          "randomize_list": true,
          "hide_automation_plugins": true
        },
        "languages": {
          "randomize": true,
          "prefer_english": true,
          "match_geolocation": true
        }
      },
      
      "network_behavior": {
        "timing": {
          "request_delays": [0.5, 3.0],
          "page_load_delays": [2.0, 8.0],
          "interaction_delays": [0.1, 2.0]
        },
        "patterns": {
          "burst_prevention": true,
          "natural_browsing": true,
          "session_continuity": true
        },
        "headers": {
          "randomize_order": true,
          "add_common_headers": true,
          "vary_accept_headers": true
        }
      }
    }
  }
}
```

## Stealth Levels

### Low Stealth
Minimal stealth features for basic protection:

```json
{
  "stealth_level": "low",
  "features": {
    "user_agent_rotation": true,
    "basic_header_randomization": true,
    "simple_delays": true
  }
}
```

### Medium Stealth
Balanced stealth and performance:

```json
{
  "stealth_level": "medium",
  "features": {
    "fingerprint_spoofing": true,
    "behavior_simulation": "basic",
    "webrtc_blocking": true,
    "referrer_spoofing": true,
    "random_delays": true
  }
}
```

### High Stealth
Advanced stealth for protected sites:

```json
{
  "stealth_level": "high",
  "features": {
    "advanced_fingerprint_spoofing": true,
    "behavior_simulation": "advanced",
    "traffic_pattern_masking": true,
    "challenge_solving": true,
    "session_simulation": true
  }
}
```

### Maximum Stealth
Highest level of stealth (slower performance):

```json
{
  "stealth_level": "maximum",
  "features": {
    "comprehensive_fingerprint_spoofing": true,
    "realistic_behavior_simulation": true,
    "advanced_traffic_masking": true,
    "captcha_solving": true,
    "human_browsing_simulation": true,
    "multiple_identity_rotation": true
  }
}
```

## Browser Fingerprint Spoofing

### Canvas Fingerprinting Protection

```json
{
  "canvas_protection": {
    "enabled": true,
    "method": "noise_injection",
    "noise_level": "medium",
    "preserve_functionality": true,
    "randomization_seed": "per_session"
  }
}
```

### WebGL Fingerprinting Protection

```json
{
  "webgl_protection": {
    "enabled": true,
    "vendor_spoofing": true,
    "renderer_spoofing": true,
    "parameter_randomization": true,
    "extension_masking": true
  }
}
```

### Audio Fingerprinting Protection

```json
{
  "audio_protection": {
    "enabled": true,
    "context_spoofing": true,
    "noise_injection": true,
    "oscillator_randomization": true
  }
}
```

### Font Fingerprinting Protection

```json
{
  "font_protection": {
    "enabled": true,
    "available_fonts_masking": true,
    "metric_spoofing": true,
    "system_font_hiding": true
  }
}
```

## Behavioral Simulation

### Mouse Movement Simulation

```json
{
  "mouse_simulation": {
    "enabled": true,
    "movement_patterns": "natural",
    "speed_variation": true,
    "pause_simulation": true,
    "click_patterns": "human_like",
    "scroll_behavior": {
      "enabled": true,
      "speed_variation": true,
      "pause_frequency": "realistic",
      "direction_changes": true
    }
  }
}
```

### Typing Pattern Simulation

```json
{
  "typing_simulation": {
    "enabled": true,
    "speed_variation": true,
    "pause_patterns": "realistic",
    "error_simulation": false,
    "backspace_patterns": true,
    "typing_rhythm": "natural"
  }
}
```

### Reading Pattern Simulation

```json
{
  "reading_simulation": {
    "enabled": true,
    "scroll_pauses": true,
    "reading_speed": "average",
    "attention_patterns": true,
    "back_navigation": "occasional"
  }
}
```

### Session Behavior

```json
{
  "session_behavior": {
    "enabled": true,
    "tab_management": {
      "multiple_tabs": false,
      "tab_switching": false,
      "background_tabs": false
    },
    "navigation_patterns": {
      "back_button_usage": "realistic",
      "bookmark_simulation": false,
      "search_behavior": true
    },
    "interaction_patterns": {
      "form_filling_delays": true,
      "button_hover_delays": true,
      "element_focus_simulation": true
    }
  }
}
```

## Traffic Pattern Masking

### Google Search Simulation

```json
{
  "google_search_simulation": {
    "enabled": true,
    "search_query_generation": true,
    "results_page_interaction": true,
    "organic_click_simulation": true,
    "search_refinement": false,
    "cache": {
      "enabled": true,
      "duration": 3600,
      "randomize_queries": true
    }
  }
}
```

### Referrer Chain Building

```json
{
  "referrer_simulation": {
    "enabled": true,
    "chain_length": [1, 3],
    "realistic_sources": [
      "google.com",
      "bing.com",
      "social_media",
      "direct"
    ],
    "landing_page_simulation": true,
    "search_term_variation": true
  }
}
```

### Session Continuity

```json
{
  "session_continuity": {
    "enabled": true,
    "cookie_persistence": true,
    "session_storage_simulation": true,
    "browsing_history_simulation": true,
    "cache_behavior": "realistic",
    "connection_reuse": true
  }
}
```

## Anti-Detection Mechanisms

### WebDriver Detection Evasion

```json
{
  "webdriver_evasion": {
    "enabled": true,
    "techniques": [
      "chrome_runtime_spoofing",
      "navigator_webdriver_removal",
      "selenium_flag_removal",
      "automation_flag_masking",
      "chrome_extension_simulation"
    ],
    "aggressive_mode": false
  }
}
```

### Bot Detection Evasion

```json
{
  "bot_detection_evasion": {
    "enabled": true,
    "cloudflare": {
      "challenge_solving": true,
      "js_challenge_timeout": 30,
      "captcha_detection": true
    },
    "imperva": {
      "enabled": true,
      "pixel_tracking_evasion": true
    },
    "distil": {
      "enabled": true,
      "behavioral_analysis_evasion": true
    },
    "generic": {
      "javascript_execution_delays": true,
      "dom_manipulation_simulation": true,
      "event_simulation": true
    }
  }
}
```

### Challenge Solving

```json
{
  "challenge_solving": {
    "enabled": true,
    "captcha": {
      "detection": true,
      "solving": false,
      "service": null,
      "timeout": 60
    },
    "javascript_challenges": {
      "enabled": true,
      "timeout": 30,
      "execution_delay": [1, 5]
    },
    "proof_of_work": {
      "enabled": true,
      "timeout": 45
    }
  }
}
```

## Resource Blocking and Optimization

### Advertisement Blocking

```json
{
  "ad_blocking": {
    "enabled": true,
    "block_lists": [
      "easylist",
      "easylist_privacy",
      "ublock_origin"
    ],
    "custom_filters": [],
    "whitelist_domains": [],
    "aggressive_blocking": false
  }
}
```

### Resource Filtering

```json
{
  "resource_filtering": {
    "enabled": true,
    "block_types": [
      "image",
      "media",
      "font",
      "websocket"
    ],
    "allow_critical": true,
    "size_limits": {
      "max_image_size": "1MB",
      "max_script_size": "5MB"
    }
  }
}
```

### Network Optimization

```json
{
  "network_optimization": {
    "compression": true,
    "cache_control": "aggressive",
    "connection_pooling": true,
    "dns_prefetch": false,
    "preload_hints": false
  }
}
```

## Geographic and Temporal Spoofing

### Geolocation Spoofing

```json
{
  "geolocation_spoofing": {
    "enabled": true,
    "mode": "fixed",
    "coordinates": {
      "latitude": 40.7128,
      "longitude": -74.0060,
      "accuracy": 100
    },
    "randomize_within_radius": 1000,
    "city_simulation": "New York"
  }
}
```

### Timezone Spoofing

```json
{
  "timezone_spoofing": {
    "enabled": true,
    "target_timezone": "America/New_York",
    "match_geolocation": true,
    "randomize_offset": false,
    "dst_handling": true
  }
}
```

### Language and Locale Spoofing

```json
{
  "locale_spoofing": {
    "enabled": true,
    "languages": ["en-US", "en"],
    "country": "US",
    "currency": "USD",
    "number_format": "US",
    "date_format": "US"
  }
}
```

## Performance Considerations

### Stealth vs Performance Tradeoffs

```json
{
  "performance_config": {
    "stealth_priority": "balanced",
    "timeout_multipliers": {
      "page_load": 1.5,
      "element_wait": 2.0,
      "script_execution": 1.2
    },
    "resource_limits": {
      "max_memory": "512MB",
      "max_cpu": 80
    },
    "optimization": {
      "lazy_loading": true,
      "image_compression": true,
      "script_minification": false
    }
  }
}
```

### Concurrent Stealth Sessions

```json
{
  "concurrency_config": {
    "max_concurrent_sessions": 3,
    "session_isolation": true,
    "resource_sharing": false,
    "staggered_launches": true,
    "launch_delay": [2, 8]
  }
}
```

## Monitoring and Detection

### Stealth Effectiveness Monitoring

```json
{
  "monitoring": {
    "enabled": true,
    "detection_alerts": true,
    "fingerprint_tracking": true,
    "behavior_analysis": true,
    "challenge_frequency": true,
    "success_rate_tracking": true
  }
}
```

### Stealth Metrics

ScraperV4 tracks stealth effectiveness:

- **Detection Rate**: Percentage of requests detected as automated
- **Challenge Frequency**: How often CAPTCHAs/challenges are encountered  
- **Fingerprint Uniqueness**: How unique the browser fingerprint appears
- **Behavior Score**: How human-like the browsing behavior appears
- **Success Rate**: Percentage of successful page loads

## Error Handling

### Stealth-Related Errors

```json
{
  "error_handling": {
    "detection_response": "rotate_identity",
    "challenge_timeout": "fallback_fetcher",
    "fingerprint_collision": "regenerate",
    "behavioral_flag": "slow_down",
    "max_retries": 3,
    "cooldown_period": 300
  }
}
```

### Fallback Strategies

```json
{
  "fallback_strategies": [
    {
      "trigger": "high_detection_rate",
      "action": "increase_stealth_level",
      "threshold": 15.0
    },
    {
      "trigger": "repeated_challenges",
      "action": "rotate_session",
      "threshold": 3
    },
    {
      "trigger": "performance_degradation",
      "action": "reduce_stealth_level",
      "threshold": 10.0
    }
  ]
}
```

## Best Practices

### Stealth Configuration Guidelines

1. **Start Conservative**: Begin with medium stealth level
2. **Monitor Detection**: Track detection rates and adjust accordingly
3. **Site-Specific Tuning**: Different sites require different approaches
4. **Performance Balance**: Balance stealth needs with speed requirements
5. **Regular Updates**: Update fingerprints and behaviors regularly

### Common Stealth Patterns

```json
{
  "patterns": {
    "e_commerce": {
      "stealth_level": "medium",
      "google_search": true,
      "session_simulation": true,
      "product_browsing": true
    },
    "social_media": {
      "stealth_level": "high",
      "mobile_simulation": true,
      "infinite_scroll": true,
      "interaction_simulation": true
    },
    "news_sites": {
      "stealth_level": "low",
      "reading_simulation": true,
      "article_scrolling": true,
      "ad_blocking": true
    },
    "protected_content": {
      "stealth_level": "maximum",
      "challenge_solving": true,
      "session_persistence": true,
      "behavioral_mimicry": true
    }
  }
}
```

## See Also

- [Environment Variables](environment-variables.md) - Global stealth environment variables
- [Proxy Settings](proxy-settings.md) - Proxy integration with stealth mode
- [Template Schema](template-schema.md) - Stealth configuration in templates
- [Scrapers Reference](../classes/scrapers.md) - Stealth fetcher implementation