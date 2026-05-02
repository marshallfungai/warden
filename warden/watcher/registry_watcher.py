"""
Registry watcher for Warden
"""

import time
import logging
from typing import Callable
from warden.docker.registry import RegistryClient


logger = logging.getLogger(__name__)

class RegistryWatcher:
    """
    Watches/Polls the registry for new images and triggers a deployment if a new image is found
    """

    def __init__(self, registry_url:str, image_name:str, image_tag:str = "latest", interval:int=1000):
        self.registry = registry
        self.interval = interval
        self.image_name = image_name
        self.image_tag = image_tag
        self.current_digest = None
        self.automatic_deployment = os.getenv("AUTOMATIC_DEPLOYMENT", "false") == "true"

    def _get_image_digest(self):
        """
        Get the digest of the image
        """
        return self.registry.get_image_digest(self.image_name, self.image_tag)

    def run(self):
        """
        Run the registry watcher
        """
        logger.info(f"Running registry watcher for {self.image_name}:{self.image_tag}")

        while True:
            new_digest = self._get_image_digest()
            if new_digest != self.current_digest:
                self.current_digest = new_digest
                logger.info(f"New image digest found for {self.image_name}:{self.image_tag}: {new_digest}")
                if self.automatic_deployment:
                    self.deploy()
                else:
                    logger.info(f"Automatic deployment is disabled. Please deploy the new image manually.")
            time.sleep(self.interval)
