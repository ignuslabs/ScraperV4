"""Proxy rotation management for stealth scraping."""

import random
import time
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class ProxyRotator:
    """Manages proxy rotation for stealth fetching."""
    
    def __init__(self, proxy_list: Optional[List[str]] = None):
        """Initialize with proxy list.
        
        Args:
            proxy_list: List of proxy URLs in format 'http://user:pass@host:port'
        """
        self.proxies = proxy_list or []
        self.current_index = 0
        self.failed_proxies = set()
        self.proxy_stats = {}
        self.last_rotation = datetime.now()
        self.rotation_interval = timedelta(seconds=30)  # Minimum time between rotations
        
        # Initialize stats for each proxy
        for proxy in self.proxies:
            self.proxy_stats[proxy] = {
                'successes': 0,
                'failures': 0,
                'last_used': None,
                'response_times': [],
                'blacklisted_until': None
            }
    
    def get_next_proxy(self) -> Optional[str]:
        """Get next working proxy in rotation.
        
        Returns:
            Next available proxy URL or None if no working proxies
        """
        if not self.proxies:
            return None
        
        # Find next working proxy
        attempts = 0
        while attempts < len(self.proxies):
            proxy = self.proxies[self.current_index]
            self.current_index = (self.current_index + 1) % len(self.proxies)
            
            # Check if proxy is blacklisted temporarily
            stats = self.proxy_stats.get(proxy, {})
            blacklisted_until = stats.get('blacklisted_until')
            if blacklisted_until and datetime.now() < blacklisted_until:
                attempts += 1
                continue
            
            # Check if proxy is permanently failed
            if proxy not in self.failed_proxies:
                # Update last used time
                self.proxy_stats[proxy]['last_used'] = datetime.now()
                self.last_rotation = datetime.now()
                return proxy
            
            attempts += 1
        
        # All proxies failed, reset failed list and try again
        if self.failed_proxies:
            logger.warning("All proxies marked as failed, resetting failed list")
            self.failed_proxies.clear()
            return self.proxies[0] if self.proxies else None
        
        return None
    
    def get_best_proxy(self) -> Optional[str]:
        """Get the best performing proxy based on statistics.
        
        Returns:
            Best proxy URL based on success rate and response time
        """
        if not self.proxies:
            return None
        
        best_proxy = None
        best_score = -1
        
        for proxy in self.proxies:
            # Skip failed or blacklisted proxies
            if proxy in self.failed_proxies:
                continue
            
            stats = self.proxy_stats.get(proxy, {})
            
            # Check blacklist
            blacklisted_until = stats.get('blacklisted_until')
            if blacklisted_until and datetime.now() < blacklisted_until:
                continue
            
            # Calculate score based on success rate and average response time
            successes = stats.get('successes', 0)
            failures = stats.get('failures', 0)
            total = successes + failures
            
            if total == 0:
                # Unused proxy, give it a neutral score
                score = 0.5
            else:
                success_rate = successes / total
                
                # Factor in response time if available
                response_times = stats.get('response_times', [])
                if response_times:
                    avg_response_time = sum(response_times) / len(response_times)
                    # Normalize response time (lower is better)
                    time_score = 1.0 / (1.0 + avg_response_time)
                    score = (success_rate * 0.7) + (time_score * 0.3)
                else:
                    score = success_rate
            
            if score > best_score:
                best_score = score
                best_proxy = proxy
        
        if best_proxy:
            self.proxy_stats[best_proxy]['last_used'] = datetime.now()
            
        return best_proxy
    
    def mark_success(self, proxy: str, response_time: Optional[float] = None):
        """Mark proxy as successful.
        
        Args:
            proxy: Proxy URL that succeeded
            response_time: Response time in seconds
        """
        if proxy not in self.proxy_stats:
            self.proxy_stats[proxy] = {
                'successes': 0,
                'failures': 0,
                'last_used': None,
                'response_times': [],
                'blacklisted_until': None
            }
        
        self.proxy_stats[proxy]['successes'] += 1
        
        # Track response time
        if response_time is not None:
            response_times = self.proxy_stats[proxy]['response_times']
            response_times.append(response_time)
            # Keep only last 10 response times
            if len(response_times) > 10:
                response_times.pop(0)
        
        # Remove from failed set if it was there
        self.failed_proxies.discard(proxy)
        
        # Clear blacklist if successful
        self.proxy_stats[proxy]['blacklisted_until'] = None
        
        logger.debug(f"Proxy {proxy} marked as successful")
    
    def mark_failed(self, proxy: str, permanent: bool = False):
        """Mark proxy as failed.
        
        Args:
            proxy: Proxy URL that failed
            permanent: If True, proxy is permanently failed
        """
        if proxy not in self.proxy_stats:
            self.proxy_stats[proxy] = {
                'successes': 0,
                'failures': 0,
                'last_used': None,
                'response_times': [],
                'blacklisted_until': None
            }
        
        self.proxy_stats[proxy]['failures'] += 1
        
        if permanent:
            self.failed_proxies.add(proxy)
            logger.warning(f"Proxy {proxy} permanently failed")
        else:
            # Temporary blacklist with exponential backoff
            failures = self.proxy_stats[proxy]['failures']
            blacklist_duration = min(300, 10 * (2 ** min(failures, 5)))  # Max 5 minutes
            self.proxy_stats[proxy]['blacklisted_until'] = datetime.now() + timedelta(seconds=blacklist_duration)
            logger.debug(f"Proxy {proxy} blacklisted for {blacklist_duration} seconds")
    
    def add_proxy(self, proxy: str):
        """Add a new proxy to the rotation pool.
        
        Args:
            proxy: Proxy URL to add
        """
        if proxy not in self.proxies:
            self.proxies.append(proxy)
            self.proxy_stats[proxy] = {
                'successes': 0,
                'failures': 0,
                'last_used': None,
                'response_times': [],
                'blacklisted_until': None
            }
            logger.info(f"Added proxy {proxy} to rotation pool")
    
    def remove_proxy(self, proxy: str):
        """Remove a proxy from the rotation pool.
        
        Args:
            proxy: Proxy URL to remove
        """
        if proxy in self.proxies:
            self.proxies.remove(proxy)
            self.failed_proxies.discard(proxy)
            if proxy in self.proxy_stats:
                del self.proxy_stats[proxy]
            logger.info(f"Removed proxy {proxy} from rotation pool")
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics for all proxies.
        
        Returns:
            Dictionary with proxy statistics
        """
        total_proxies = len(self.proxies)
        working_proxies = total_proxies - len(self.failed_proxies)
        
        proxy_details = []
        for proxy in self.proxies:
            stats = self.proxy_stats.get(proxy, {})
            successes = stats.get('successes', 0)
            failures = stats.get('failures', 0)
            total = successes + failures
            
            proxy_info = {
                'proxy': proxy,
                'status': 'failed' if proxy in self.failed_proxies else 'working',
                'successes': successes,
                'failures': failures,
                'success_rate': (successes / total * 100) if total > 0 else 0,
                'last_used': stats.get('last_used'),
                'blacklisted_until': stats.get('blacklisted_until')
            }
            
            # Add average response time if available
            response_times = stats.get('response_times', [])
            if response_times:
                proxy_info['avg_response_time'] = sum(response_times) / len(response_times)
            
            proxy_details.append(proxy_info)
        
        return {
            'total_proxies': total_proxies,
            'working_proxies': working_proxies,
            'failed_proxies': len(self.failed_proxies),
            'last_rotation': self.last_rotation,
            'proxy_details': proxy_details
        }
    
    def reset_statistics(self):
        """Reset all proxy statistics."""
        self.failed_proxies.clear()
        for proxy in self.proxies:
            self.proxy_stats[proxy] = {
                'successes': 0,
                'failures': 0,
                'last_used': None,
                'response_times': [],
                'blacklisted_until': None
            }
        logger.info("Reset all proxy statistics")
    
    def validate_proxies(self, test_url: str = "http://httpbin.org/ip") -> Dict[str, bool]:
        """Validate all proxies by testing them.
        
        Args:
            test_url: URL to test proxies against
            
        Returns:
            Dictionary mapping proxy to validation status
        """
        import requests
        
        validation_results = {}
        
        for proxy in self.proxies:
            try:
                # Test proxy with a simple request
                proxies = {'http': proxy, 'https': proxy}
                response = requests.get(test_url, proxies=proxies, timeout=10)
                
                if response.status_code == 200:
                    validation_results[proxy] = True
                    self.mark_success(proxy)
                else:
                    validation_results[proxy] = False
                    self.mark_failed(proxy)
                    
            except Exception as e:
                logger.debug(f"Proxy {proxy} validation failed: {e}")
                validation_results[proxy] = False
                self.mark_failed(proxy)
        
        return validation_results