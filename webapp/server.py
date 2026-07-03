import time
from pathlib import Path

from flask import Flask, Response, jsonify, send_from_directory

from webapp.runtime import SkyEyesRuntime


BASE_DIR = Path(__file__).resolve().parent


def create_app(runtime=None):
    app = Flask(
        __name__,
        static_folder=str(BASE_DIR / "static"),
        static_url_path="/static"
    )
    app.config["runtime"] = runtime or SkyEyesRuntime()

    @app.before_request
    def ensure_runtime_started():
        app.config["runtime"].start()

    @app.route("/")
    def index():
        return send_from_directory(BASE_DIR / "static", "index.html")

    @app.route("/video_feed")
    def video_feed():
        return Response(
            _frame_stream(app.config["runtime"]),
            mimetype="multipart/x-mixed-replace; boundary=frame"
        )

    @app.route("/api/status")
    def status():
        return jsonify(app.config["runtime"].get_status())

    @app.route("/api/alarms")
    def alarms():
        return jsonify(app.config["runtime"].get_alarms())

    @app.route("/api/snapshot")
    def snapshot():
        frame = app.config["runtime"].get_frame()

        if frame is None:
            return Response(status=204)

        return Response(frame, mimetype="image/jpeg")

    return app


def _frame_stream(runtime):
    while True:
        frame = runtime.get_frame()

        if frame is None:
            time.sleep(0.1)
            continue

        yield (
            b"--frame\r\n"
            b"Content-Type: image/jpeg\r\n\r\n" + frame + b"\r\n"
        )


if __name__ == "__main__":
    app = create_app()
    app.run(host="127.0.0.1", port=5000, threaded=True)
