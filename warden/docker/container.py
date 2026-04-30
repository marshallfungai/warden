"""
Dynamic container creation and management
"""

import docker
import logging
from typing import Optional, Dict

from warden.docker.client import DockerClient

logger = logging.getLogger(__name__)

class ContainerInstance:
    """ Dynamically creates and manages container instnace."""

    def __init__(
        self, 
        name:str, 
        image:str, 
        tags:str, 
        recreate:bool=False, 
        port_mapping: Optional[Dict[int, int]] = None, 
        environment:Optional[dict]=None, 
        volumes:Optional[dict]=None,
        network:str="warden-network"
    ):
        self.client = DockerClient()

        self.name = name
        self.image = image
        self.ports = [port for port in port_mapping.values()] if port_mapping else []
        self.environment = environment if environment else {}
        self.volumes = volumes if volumes else {}
        self.tags = tags
        self.network = network
        
        self._create_container(name, image, tags, recreate, port_mapping, environment, volumes, self.network)
        logger.info(f"Container Instance {name} initialized")

    
    def _create_container(
        self, 
        name:str,
        image:str, 
        tags:str = "latest",
        recreate:bool=False,
        port_mapping: Optional[Dict[int, int]] = None,
        environment:Optional[dict]=None, 
        volumes:Optional[dict]=None,
        network:str="warden-network"
      ):
      
        """Create a new container"""
        if self.container_exists(name):
            if recreate:
                self.stop_container()
                self.remove_container()
                logger.info(f"Removed old container {name}")
            else:
                logger.info(f"Container {name} already exists, reusing it")
                return self.client.get(self.name)

        try:
            self.client.create(name, image, tags, port_mapping, environment, volumes, network)
        except docker.errors.APIError as e:
            logger.error(f"Error pulling image {image}:{tags}: {e}")
            raise e
        except Exception as e:
            logger.error(f"Error pulling image {image}:{tags}: {e}")
            raise e
    
    def get_logs(self):
        """Get container logs"""
        try:
            return self.client.logs(self.name)
        except docker.errors.APIError as e:
            logger.error(f"Error getting logs for container {self.name}: {e}")
            return None
        except Exception:
            logger.error(f"Error getting logs for container {self.name}")
            return None

    def start(self):
        """Start a container"""
        try:
            return self.client.start(self.name)
        except docker.errors.APIError as e:
            logger.error(f"Error starting container {self.name}: {e}")
            return False
        except Exception:
            logger.error(f"Error starting container {self.name}")
            return False

    def container_exists(self)->bool:
        """Check if container exists"""
        return True if self.client.get(self.name) else False
    
    def stop(self)->bool:
        """Stop a container"""
        try:
            return self.client.stop(self.name)
        except docker.errors.APIError as e:
            logger.error(f"Error stopping container {self.name}: {e}")
            return False
        except Exception:
            logger.error(f"Error stopping container {self.name}")
            return False

    def remove(self)-> bool:
        """Remove a container"""
        try:
            return self.client.remove(self.name)
        except docker.errors.APIError as e:
            logger.error(f"Error removing container {self.name}: {e}")
            return False
        except Exception:
            logger.error(f"Error removing container {self.name}")
            return False

    # def get_health(self, app_type:str="nextjs")->bool:
    #     """Get container health"""
    #     try:
    #         return self.client.health(self.name)
    #     except docker.errors.APIError as e:
    #         logger.error(f"Error getting health for container {self.name}: {e}")
    #         return False
    #     except Exception:
    #         logger.error(f"Error getting health for container {self.name}")
    #         return False
 