"""
Docker client wrapper
"""

import docker
import os
import logging
from typing import Dict, List, Optional
from docker.models.containers import Container

logger = logging.getLogger(__name__)

class DockerClient:
    
    def __init__(self):
        self.client = docker.from_env()
        logger.info("Docker client initialized")

    def create(
        self, 
        name:str, 
        image:str, 
        tags:str = "latest", 
        port_mapping: Optional[Dict[int, int]] = None, 
        environment:Optional[dict]=None, 
        volumes:Optional[dict]=None,
        network:str="warden-network"
        )->Container | None:

        """Create a new container"""
        
        network = self.network(network)
        if not network:
            logger.error(f"Error creating container {name}: Network {network} not found")
            return None
            
        ports = port_mapping or None
        try:
            return self.client.containers.create(
                image=image,
                name=name,
                ports=ports,
                environment=environment,
                volumes=volumes,
                network=network,
            )
        except docker.errors.APIError as e:
            logger.error(f"Error creating container {name}: {e}")
            return None

    def status(self, name: str) -> str | None:
        """Get container status"""
        container = self.get(name)
        if not container:
            return None
        return container.status

    def get(self, name:str)->Container | None:
        """Get container by name"""
        try:
            return self.client.containers.get(name)
        except docker.errors.NotFound:
            return None    
        except docker.errors.APIError as e:
            logger.error(f"Error getting container {name}: {e}")
            return None
    
    def logs(self, name:str, tag:s)->bytes | None:
        """Get container logs"""
        try:
            container = self.get(name)
            if not container:
                return None
            return container.logs()
        except docker.errors.APIError as e:
            logger.error(f"Error getting logs for container {name}: {e}")
            return None

    def start(self, name:str)->bool:
        """Start a container"""
        try:
            container = self.get(name)
            if not container:
                return False
            container.start()
            return True
        except docker.errors.APIError as e:
            logger.error(f"Error starting container {name}: {e}")
            return False


    def stop(self, name: str)->bool:
        """Stop a container"""
        try:
            container = self.get(name)
            if not container:
                return False
            container.stop()
            return True
        except docker.errors.APIError as e:
            logger.error(f"Error stopping container {name}: {e}")
            return False

    def remove(self, name: str) -> bool:
        """Remove a container"""
        try:
            container = self.get(name)
            if not container:
                return False
            container.remove()
            return True
        except docker.errors.APIError as e:
            logger.error(f"Error removing container {name}: {e}")
            return False

    def ports(self, name:str)->List[int]:
        """Get container ports"""
        try:
            container = self.get(name)
            if not container or not container.ports:
                return []
            published_ports: List[int] = []
            for bindings in container.ports.values():
                if bindings:
                    for binding in bindings:
                        host_port = binding.get("HostPort")
                        if host_port:
                            published_ports.append(int(host_port))
            return published_ports
        except docker.errors.APIError as e:
            logger.error(f"Error getting ports for container {name}: {e}")
            return []

    def network(self, name:str)->str:
        """Ensure network exists"""
        try:
            return self.client.networks.get(name)
        except docker.errors.NotFound:
            return self.client.networks.create(name)
        except docker.errors.APIError as e:
            logger.error(f"Error getting network {name}: {e}")
            return None

