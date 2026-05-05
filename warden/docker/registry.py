"""
Docker registry wrapper
"""

import os
import time
import random
import docker
from docker.models.images import Image
import logging
from typing import Callable, TypeVar


logger = logging.getLogger(__name__)
T = TypeVar("T")

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
    
    def login(self, registry:str, username:str|None, password:str|None):
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

    def get_image_digest(self, image:str, tag:str)->str|None:
        """Get the digest of an image"""
        try:
            full_image = f"{self.registry}/{image}:{tag}"
            image = self.retry_with_backoff(lambda: self.client.images.get(full_image))
            if image.attrs['RepoDigests'][0] is not None:
                return image.attrs['RepoDigests'][0].split("@")[1]
            else:
                return image.id # use the image id as the digest
        except docker.errors.APIError as e:
            logger.error(f"Error getting image digest for {image}:{tag}: {e}")
            return None
    
    def retry_with_backoff(self, func: Callable[[], T], retries: int = 3, delay: int = 1) -> T:
        """
        Retry a function with backoff
        """
        last_exception = None
        for attempt in range(retries):
            try:
                return func()
            except Exception as e:
                last_exception = e
                if attempt == retries - 1:
                    raise last_exception
                time.sleep(delay * (2 ** attempt) + random.uniform(0, 1))
        return last_exception
    