"""
Supported Health Check Endpoints
"""

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

    def get_health_endpoint(framework: str) -> str:
        """Get default health endpoint for a framework"""
        endpoints = {
            "nextjs": HealthEndpoint.NEXTJS,
            "php": HealthEndpoint.PHP_GATEWAY,
            "fastapi": HealthEndpoint.FASTAPI,
            "flask": HealthEndpoint.FLASK,
            "express": HealthEndpoint.EXPRESS,
            "spring": HealthEndpoint.SPRING,
            "rails": HealthEndpoint.RAILS,
        }
        return endpoints.get(framework.lower(), HealthEndpoint.NEXTJS)

    def parse_health_response(data: Dict[str, Any]) -> bool:
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