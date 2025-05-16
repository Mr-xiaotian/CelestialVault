# inst_task/task_web.py

import threading
from flask import Flask, jsonify, render_template

class TaskWebServer:
    from .task_tree import TaskTree
    def __init__(self, task_tree: TaskTree, host='127.0.0.1', port=5000):
        self.task_tree = task_tree
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
            for (err, tag), task_list in self.task_tree.get_final_error_dict().items():
                for task in task_list:
                    errors_list.append({
                        "error": err,
                        "node": tag,
                        "task_id": str(task),
                        "timestamp": "2024-01-01T00:00:00Z"
                    })
            return jsonify(errors_list)

    def start(self):
        def run():
            self.app.run(host=self.host, port=self.port, debug=False, use_reloader=False)
        self.thread = threading.Thread(target=run, daemon=True)
        self.thread.start()
