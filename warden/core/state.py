"""
State management for Warden
"""

import os
import json
import redis
import logging
from typing import Optional

from warden.docker.client import DockerClient
from warden.nginx.controller import APP_STATE

logger = logging.getLogger(__name__)


class DeploymentState:
    """
     Stores deployment state to Redis.
     This allows us to track the state of the deployment and rollback to a previous version if needed.
    """

    def __init__(self, app_name:str = "demo-app"):
        self.app_name = app_name
        self.redis_client = self._get_redis_client()


    def _get_redis_client(self)->redis.Redis | None:
        """Get Redis Client"""
        try:
            docker_client = DockerClient()
            redis_host = docker_client.get("redis").attrs["NetworkSettings"]["Networks"]["warden-network"]["IPAddress"]
            redis_port = docker_client.get("redis").attrs["NetworkSettings"]["Ports"]["6379/tcp"][0]["HostPort"]
            redis_db = int(os.getenv("REDIS_DB", 0))
            redis_url = f"redis://{redis_host}:{redis_port}"
            
            logger.info(f"Redis URL: {redis_url}")
            return redis.Redis(host=redis_host,port=redis_port, db=redis_db)
        except Exception as e:
          return None

    def _get_redis_key(self, key:APP_STATE):
        """Get Redis Key"""
        return f"{self.app_name}:{key}"

    def _get_redis_value(self, key:str):
        """Get Redis Value"""
        return self.redis_client.get(self._get_redis_key(key))

    def set_active(self, color:APP_STATE):
        """Set active service color (blue or green)"""
        if self.redis.client.ping():
            self.redis_client.set(self._get_redis_key("active"), color)
        else:
            logger.error("Redis client is not connected")
            raise Exception("Redis client is not connected")
    
    def get_active(self)->str:
        """Get active service color (blue or green)"""
        if self.redis.client.ping():
            return self._get_redis_value("active")
        else:
            logger.error("Redis client is not connected")
            raise Exception("Redis client is not connected")