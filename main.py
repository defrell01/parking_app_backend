import os
from fastapi.middleware.wsgi import WSGIMiddleware
from uvicorn import Config, Server
from gunicorn.app.base import BaseApplication
from app import app


def run_asgi():
    uvicorn_config = Config(app=app, host="0.0.0.0", port=8000)
    server = Server(uvicorn_config)
    server.run()


def run_wsgi():
    class WSGIServer(BaseApplication):
        def __init__(self, app, options=None):
            self.options = options or {}
            self.application = WSGIMiddleware(app)

            super().__init__()

        def load_config(self):
            for key, value in self.options.items():
                self.cfg.set(key, value)

        def load(self):
            return self.application

    options = {
        "bind": "0.0.0.0:8000",
        "workers": os.cpu_count() * 2 + 1,
    }
    server = WSGIServer(app, options=options)
    server.run()


if __name__ == "__main__":
    if os.getenv("USE_WSGI"):
        run_wsgi()
    else:
        run_asgi()
