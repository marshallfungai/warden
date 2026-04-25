"""
Docker registry wrapper
"""

import os
import docker
from docker.models.images import Image
import logging


logger = logging.getLogger(__name__)

class RegistryClient:
    """
     Container registry client supporting:
     - Docker Registry (localhost:5000)
     - Harbor
     - Docker Hub
    """

    def __init__(self):
        self.client = docker.from_env()
        self.registry = os.getenv("REGISTRY_URL", "localhost:5000")
        self.username = os.getenv("REGISTRY_USERNAME", None)
        self.password = os.getenv("REGISTRY_PASSWORD", None)

        self.login(self.registry, self.username, self.password)
    
    def login(self, registry:str, username:str, password:str):
        """Login to the registry"""
        try:
            logger.info(f"Logging in to {registry}")
            if username and password:
                self.client.login(username, password, registry)
            else:
                self.client.login(registry)
            
        except docker.errors.APIError as e:
            logger.error(f"Error logging in to {registry}: {e}")
            
    
    def pull(self, image:str, tag:str)->Image|None:
        """Pull an image from the registry"""
        try:
            full_image = f"{self.registry}/{image}:{tag}"
            image =self.client.images.pull(full_image)
            logger.info(f"Pulled image {image}:{tag} from {self.registry}")
            return image
        except docker.errors.APIError as e:
            logger.error(f"Error pulling image {image}:{tag}: {e}")
            return None