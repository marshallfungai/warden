"""
Deployment-specific exception hierarchy.
"""


class DeploymentError(Exception):
    """Base class for expected deployment failures."""


class ImagePullError(DeploymentError):
    """Raised when pulling the deployment image fails."""


class ContainerCreateError(DeploymentError):
    """Raised when creating or finding the idle container fails."""


class HealthCheckError(DeploymentError):
    """Raised when health checks fail for the new container."""


class TrafficSwitchError(DeploymentError):
    """Raised when proxy traffic switch fails."""

    
