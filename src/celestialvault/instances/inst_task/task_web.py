# inst_task/task_web.py

import logging, os
from flask import Flask, jsonify, render_template, request


class TaskWebServer:
    def __init__(self, host="0.0.0.0", port=5000):
        self.app = Flask(__name__, static_folder="static", template_folder="templates")
        self.host = host
        self.port = port
        self._setup_routes()

        # 用于存储状态、结构、错误信息
        self.status_store = {}
        self.structure_store = []
        self.error_store = []

        self.report_interval = 5

    def _setup_routes(self):
        app = self.app

        @app.route("/")
        def index():
            return render_template("index.html")

        # ---- 展示接口 ----
        @app.route("/api/get_structure")
        def get_structure():
            return jsonify(self.structure_store)

        @app.route("/api/get_status")
        def get_status():
            return jsonify(self.status_store)

        @app.route("/api/get_errors")
        def get_errors():
            return jsonify(self.error_store)
        
        @app.route("/api/get_interval", methods=["GET"])
        def get_interval():
            return jsonify({"interval": self.report_interval})

        # ---- 接收接口 ----
        @app.route("/api/push_structure", methods=["POST"])
        def push_structure():
            self.structure_store = request.json
            return jsonify({"ok": True})

        @app.route("/api/push_status", methods=["POST"])
        def push_status():
            self.status_store = request.json
            return jsonify({"ok": True})

        @app.route("/api/push_errors", methods=["POST"])
        def push_errors():
            self.error_store = request.json
            return jsonify({"ok": True})
        
        @app.route("/api/push_interval", methods=["POST"])
        def push_interval():
            try:
                data = request.get_json(force=True)
                interval = float(data.get("interval", 5.0))
                self.report_interval = max(1.0, min(interval / 1000.0, 60.0))  # 限制 1~60s
                return "Interval updated", 200
            except Exception as e:
                return f"Invalid interval: {e}", 400

        @app.route("/shutdown", methods=["POST"])
        def shutdown():
            func = request.environ.get("werkzeug.server.shutdown")
            if func:
                func()
                return "Server shutting down..."
            else:
                os._exit(0)

    def start_server(self):
        # logging.getLogger("werkzeug").setLevel(logging.ERROR)
        self.app.run(host=self.host, port=self.port, debug=False, use_reloader=False)

    def stop_server(self):
        import requests
        try:
            url = f"http://{self.host}:{self.port}/shutdown"
            requests.post(url, timeout=2)
        except Exception as e:
            print(f"[stop_server] 停止 Web 服务时发生异常: {e}")

if __name__ == "__main__":
    server = TaskWebServer(port=5000)
    server.start_server()