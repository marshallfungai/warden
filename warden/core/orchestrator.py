"""
Core deployment orchestrator for Warden
"""

import time
import os
import logging
from dataclasses import dataclass
from typing import Optional

from warden.docker.registry import RegistryClient
from warden.docker.client import DockerClient
from warden.docker.container import ContainerInstance
from warden.core.state import DeploymentState
from warden.core.errors import (
    DeploymentError,
    ImagePullError,
    ContainerCreateError,
    TrafficSwitchError,
)
from warden.nginx.controller import NginxController
from warden.nginx.controller import APP_STATE
from warden.health.endpoints import HealthEndpoints
from warden.health.checker import HealthChecker

logger = logging.getLogger(__name__)


class Orchestrator:
    """
    Orchestrates the deployment of a service with zero downtime.
    - pulls the image from the registry
    - creates the container
    - starts the container
    - waits for the container to be healthy
    - switches the upstream to the new service
    - removes the old service
    """


    def __init__(self):

        # dependencies
        self.registry = RegistryClient()
        self.docker_client = DockerClient()
        self.nginx_controller = NginxController()
        self.state = DeploymentState()

        # configuration
        self.app_name = os.getenv("APP_NAME", "demo-app")
        self.image_name = os.getenv("IMAGE_NAME", "demo-app")
        self.image_tag = os.getenv("IMAGE_TAG", "latest")
        self.image_registry = os.getenv("REGISTRY_TYPE", "dockerhub")
        self.image_registry_url = os.getenv("REGISTRY_URL", "dockerhub")
        self.image_username = os.getenv("REGISTRY_USERNAME", None)
        self.image_password = os.getenv("REGISTRY_PASSWORD", None)
        self.default_container_environment = self._get_container_environment(self.app_type)
        # current state
        self.active_service = self.state.get_active()
        self.idle_service = "green" if self.active_service == "blue" else "blue"

        logger.info(f"Initializing Orchestrator for {self.app_name}")
        logger.info(f"Active service: {self.active_service}")
        logger.info(f"Idle service: {self.idle_service}")

    def deploy(self, version:str|None=None):
        """ 
        Deploy a new version of the service
        """
        start_time = time.time()
        version = version or self.image_tag

        logger.info("="*50)
        logger.info(f"Deploying new version {version} of {self.app_name} -> {self.idle_service}")
        logger.info("="*50)

        try:
            # 1. Pull the image from the registry
            image  = self.registry.pull(self.image_name, version)
            if not image:
                raise ImagePullError(f"Failed to pull image {self.image_name}:{version}")

            # 2. Create the idle service container
            containerInstance = self._create_container(image, version,environment=self.default_container_environment)
            if not containerInstance.container_exists():
                logger.error(f"Failed to create container {self.idle_service}")
                raise ContainerCreateError(f"Failed to create container {self.idle_service}")

            # 3. Start the idle service container
            self._start_idle_service(self.idle_service)

            # 4. Wait for the idle service to be healthy
            #self._wait_for_health(containerInstance)

            # 5. Switch the upstream to the idle service
            if not self._switch_traffic():
                raise TrafficSwitchError(f"Failed to switch traffic to {self.idle_service}")

            # 6. Stop the old active service
            self._stop_old_service()

            # 7. Remove the old service
            self._remove_old_service()

            # 8. Update the state
            self.state.set_active(self.idle_service)
        except DeploymentError as e:
            logger.error(f"Deployment failed: {e}")
            self._rollback()
            raise
        except Exception as e:
            logger.error(f"Failed to deploy new version {version} of {self.app_name} -> {self.idle_service}: {e}")
            self._rollback()
        finally:
            logger.info(f"Deployment of new version {version} of {self.app_name} -> {self.idle_service} completed in {time.time() - start_time} seconds")
            logger.info("="*50)
            logger.info(f"Deployment of new version {version} of {self.app_name} -> {self.idle_service} completed in {time.time() - start_time} seconds")


    def _create_container(self, image:Image, version:str):
        """
        Create the container
        """
        container = ContainerInstance(
            name=f"{self.app_name}-{self.idle_service}",
            image=image,
            tags=version,
        )
        
        return container

    # def _wait_for_health(self, containerInstance:ContainerInstance):
    #     """
    #     wait for the container to be healthy
    #     """

    #     container_health = containerInstance.get_health()

    def _get_service(self, service_color:APP_STATE)->ContainerInstance:
        """
        Get the service container instance
        """
        return ContainerInstance(
            name=f"{self.app_name}-{service_color}",
            image=self.image_name,
            tags=self.image_tag,
        )

    def _start_idle_service(self):
        """
        Start the idle service only if it exists
        """
        logger.info(f"Starting idle service {self.idle_service}")
        container = self._get_service(self.idle_service)
        if container.container_exists():
            container.start()
            logger.info(f"Idle service {self.idle_service} started")
        else:
            logger.error(f"Idle service {self.idle_service} not found")
        logger.info(f"Idle service {self.idle_service} started")
        
    
    def _switch_traffic(self):
        """
        Switch the traffic to the target service
        """

        logger.info(f"Switching traffic to {self.idle_service}")
        return self.nginx_controller.switch_upstream(self.idle_service)
    
    def _stop_old_service(self):
        """
        Stop the old service
        """
        logger.info(f"Stopping old service {self.active_service}")
        container = self._get_service(self.active_service)
        if container.container_exists():
            container.stop()
            logger.info(f"Old service {self.active_service} stopped")
        else:
            logger.error(f"Old service {self.active_service} not found")
        logger.info(f"Old service {self.active_service} stopped")
    
    def _remove_old_service(self):
        """
        Remove the old service
        """
        logger.info(f"Removing old service {self.active_service}")
        container = self._get_service(self.active_service)
        if container.container_exists():
            container.remove()
            logger.info(f"Old service {self.active_service} removed")
        else:
            logger.error(f"Old service {self.active_service} not found")

    def _rollback(self):
        """
        Rollback to the previous version
        """
        logger.info(f"Rolling back to the previous version of {self.app_name}")
        self._get_service(self.active_service).start()
        self._get_service(self.idle_service).stop()
        self._get_service(self.idle_service).remove()
        self.state.set_active(self.active_service)
    
    
    def _get_container_environment(self, app_type:str)->dict:
        """
        Get the container environment
        """
        if app_type == "nextjs":
            return {
                "NODE_ENV": "production",
                "SERVICE_COLOR": active,
                "APP_VERSION": self.image_tag,
            }
        elif app_type == "flask":
            return {
                "FLASK_ENV": "production",
                "SERVICE_COLOR": active,
                "APP_VERSION": self.image_tag,
            }
        elif app_type == "django":
            return {
                "DJANGO_ENV": "production",
                "SERVICE_COLOR": active,
                "APP_VERSION": self.image_tag,
            }
        elif app_type == "fastapi":
            return {
                "FASTAPI_ENV": "production",
                "SERVICE_COLOR": active,
                "APP_VERSION": self.image_tag,
            }
        elif app_type == "rust":
            return {
                "RUST_ENV": "production",
                "SERVICE_COLOR": active,
                "APP_VERSION": self.image_tag,
            }
        elif app_type == "golang":
            return {
                "GOLANG_ENV": "production",
                "SERVICE_COLOR": active,
                "APP_VERSION": self.image_tag,
            }
        elif app_type == "python":
            return {
                "PYTHON_ENV": "production",
                "SERVICE_COLOR": active,
                "APP_VERSION": self.image_tag,
            }
        elif app_type == "nodejs":
            return {
                "NODE_ENV": "production",
                "SERVICE_COLOR": active,
                "APP_VERSION": self.image_tag,
            }
        elif app_type == "express":
            return {
                "EXPRESS_ENV": "production",
                "SERVICE_COLOR": active,
                "APP_VERSION": self.image_tag,
            }
        elif app_type == "ruby":
            return {
                "RUBY_ENV": "production",       
                "SERVICE_COLOR": active,
                "APP_VERSION": self.image_tag,
            }
        elif app_type == "php":
            return {
                "PHP_ENV": "production",
                "SERVICE_COLOR": active,
                "APP_VERSION": self.image_tag,
            }
        else:
            return {
                "APP_ENV": "production",
                "SERVICE_COLOR": active,
                "APP_VERSION": self.image_tag,
            }   
        
