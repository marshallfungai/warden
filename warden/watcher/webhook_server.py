"""
Webhook server for Warden
"""

import logging
import json
from threading import Thread
from typing import Callable

from flask import Flask, request, jsonify

logger = logging.getLogger(__name__)

app = Flask(__name__)

class WebhookServer:
    """
    HTTP server that accepts deployment requests from the user
    """

    def __init__(self, port:int=5000, on_deploy:Callable[[str], None]=None,, on_rollback:Callable[[str], None]=None):
        self.port = port
        self.on_deploy = on_deploy
        self.on_rollback = on_rollback
        self.server_thread = None
    
    def _run_server(self):
        """
        Run the webhook server
        """
        
        @app.route("/deploy", methods=["POST"])
        def deploy():
            data = request.get_json()
            tag = data.get("tag", "latest")

            if self.on_deploy:
                Thread(target=self.on_deploy, args=(tag,)).start()
            
            return jsonify({"status": "success", "message": "Deployment request received"}), 202

        @app.route("rollback", methods=["POST"])
        def rollback():
            logger.info("Rollback request received")
            if self.on_rollback:
                Thread(target=self.on_rollback, args=()).start()
            return jsonify({"status": "success", "message": "Rollback request received"}), 202

        @app.route("status", methods=["GET"])
        def status():
            return jsonify({"status": "success", "message": "Status request received"}), 200
        
        app.run(host="0.0.0.0", port=self.port)

    
    def run(self):
        """
        Start the webhook server
        """
        logger.info(f"Starting webhook server on port {self.port}")
        self.server_thread = Thread(target=self._run_server)
        self.server_thread.start()