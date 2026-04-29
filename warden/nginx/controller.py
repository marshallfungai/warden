import os
import docker
import logging
from dataclasses import dataclass
from typing import Literal

logger = logging.getLogger(__name__)


APP_STATE = Literal["blue", "green"] # allows us to differentiate between active and idle services

class NginxController:
    """
    Controls nginx routing based on deployment state.
    - by rewriting the nginx.conf file
    - by reloading nginx
    """

    def __init__(self):
        self.client = docker.from_env()
        self.nginx_container = os.getenv("PROXY_CONTAINER_NAME", "proxy")
        self.app_name = os.getenv("APP_NAME", "demo-app")
        self.upstream_config = os.getenv("UPSTREAM_CONFIG", "/etc/nginx/configs/upstream.conf")

    def switch_upstream(self, target:APP_STATE):
        """
          Switch the upstream to the target service (blue or green)
        """
*
        config = f"""
        upstream backend{{
            server {self.app_name}-{target}:80;
        }}
        """
        with open(self.upstream_config, "w") as f:
            f.write(config)
        
        if self.reload_nginx():
            logger.info(f"Nginx reloaded successfully")
        else:
            logger.error(f"Failed to reload nginx")
            # raise Exception("Failed to reload nginx")


    def reload_nginx(self):
        """Reload nginx to apply the new configuration"""
        try:
            self.client.exec_run(f"nginx -t", container=self.nginx_container)
            result = self.client.exec_run(f"nginx -s reload", container=self.nginx_container)
            if result.exit_code == 0:
                return True
            else:
                return False
        except Exception as e:
            logger.error(f"Error reloading nginx: {e}")
            return False
    