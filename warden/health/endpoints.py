"""
Supported Health Check Endpoints
"""

from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

class HealthEndpoints:
    """Common health check endpoints"""

    NEXTJS = "/api/health"
    FLASK = "/health"
    DJANGO = "/health/"
    FASTAPI = "/health/"
    RUST = "/health/"
    GOLANG = "/health/"
    PYTHON = "/health/"
    NODEJS = "/health/"
    EXPRESS = "/health/"
    RUBY = "/health/"
    PHP = "/health/"
    PHP_GATEWAY = "/health/"
    SPRING = "/actuator/health"
    RAILS = "/health/"

    def get_health_endpoint(self, framework: str) -> str:
        """Get default health endpoint for a framework"""
        endpoints = {
            "nextjs": HealthEndpoints.NEXTJS,
            "php": HealthEndpoints.PHP_GATEWAY,
            "fastapi": HealthEndpoints.FASTAPI,
            "flask": HealthEndpoints.FLASK,
            "express": HealthEndpoints.EXPRESS,
            "spring": HealthEndpoints.SPRING,
            "rails": HealthEndpoints.RAILS,
        }
        return endpoints.get(framework.lower(), HealthEndpoints.NEXTJS)

    def parse_health_response(self, data: Dict[str, Any]) -> bool:
        """
        Parse health response from various frameworks.
        Returns True if healthy, False otherwise.
        """
        # Next.js format
        if data.get("status") == "healthy":
            return True
        if data.get("status") == "ok":
            return True

        # FastAPI / Spring format
        if data.get("status") == "UP":
            return True

        # Generic format
        if data.get("healthy") is True:
            return True

        # Default - if status field exists and is not "unhealthy"
        if data.get("status") and data.get("status") != "unhealthy":
            return True

        return False