"""
Health checker with retries
"""

import time
import requests
from dataclasses import dataclass, field
import logging

logger = logging.getLogger(__name__)

@dataclass
class HealthCheckConfig:
    url:str
    method:str="GET"
    timeout:int=10
    retries:int=3
    delay:int=1
    headers:dict = field(default_factory=dict)

class HealthChecker:
    """Check the health of a service"""

    def check(self, config:HealthCheckConfig)->bool:
        for attempt in range(config.retries):
            try:
                response = requests.request(config.method, config.url, timeout=config.timeout, headers=config.headers)
                if response.status_code == 200:
                    return True
                
                logger.warning(f"Health check returned non-200 status: {response.status_code}, attempt {attempt + 1} of {config.retries}")
                
            except requests.exceptions.RequestException as e:
                logger.error(f"Error checking for health: {e}")

            if attempt < config.retries - 1:
                time.sleep(config.delay)
            else:
                logger.error(f"Health check failed after {config.retries} attempts")
        return False