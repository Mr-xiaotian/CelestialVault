# inst_task/task_web.py

import threading, os, logging, requests
from flask import Flask, jsonify, render_template, request

class TaskWebServer:
    # from .task_tree import TaskTree
    def __init__(self, task_tree, host='0.0.0.0', port=5000):
        from .task_tree import TaskTree
        self.task_tree: TaskTree = task_tree
        self.app = Flask(__name__, static_folder="static", template_folder="templates")
        self.host = host
        self.port = port
        self._setup_routes()
        self.thread = None

    def _setup_routes(self):
        app = self.app

        @app.route("/")
        def index():
            return render_template("index.html")

        @app.route("/api/structure")
        def structure():
            return jsonify(self.task_tree.format_structure_list())

        @app.route("/api/status")
        def status():
            return jsonify(self.task_tree.get_status_dict())

        @app.route("/api/errors")
        def errors():
            errors_list = []
            self.task_tree.handle_final_error_dict()
            for (err, tag), task_list in self.task_tree.get_fail_by_error_dict().items():
                for task in task_list:
                    errors_list.append({
                        "error": err,
                        "node": tag,
                        "task_id": str(task),
                        "timestamp": "2024/1/1 08:00:00"
                    })
            return jsonify(errors_list)
        
        @app.route("/shutdown", methods=["POST"])
        def shutdown():
            func = request.environ.get("werkzeug.server.shutdown")
            if func:
                func()
                return "Server shutting down..."
            else:
                os._exit(0)  # 强制关闭整个进程

    def start_server(self):
        def run():
            logging.getLogger('werkzeug').setLevel(logging.ERROR)
            self.app.run(host=self.host, port=self.port, debug=False, use_reloader=False)
        
        self.thread = threading.Thread(target=run)
        self.thread.start()

    def stop_server(self):
        try:
            url = f"http://{self.host}:{self.port}/shutdown"
            requests.post(url, timeout=2)
        except Exception as e:
            print(f"[stop_server] 停止 Web 服务时发生异常: {e}")
        finally:
            if self.thread:
                self.thread.join(timeout=5)
                self.thread = None