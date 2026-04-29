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
from warden.nginx.controller import NginxController
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

            # 2. Create the idle service container
            containerInstance = self._create_container(image, version)

            # 3. Start the idle service container
            containerInstance.start()

            # 4. Wait for the idle service to be healthy
            #self._wait_for_health(containerInstance)

            # 5. Switch the upstream to the idle service
            self.nginx_controller.switch_upstream(self.idle_service)

            # 6. Stop the old active service
            self.active_service.stop()
    
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

    def _get_service(self, service_name:str)->ContainerInstance:
        """
        Get the service container instance
        """
        return ContainerInstance(
            name=f"{self.app_name}-{service_name}",
            image=self.image_name,
            tags=self.image_tag,
        )

