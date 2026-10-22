import os

from flask import Flask

from controller import NumberController
from logger import setup_logger
from repository import NumberRepository
from service import NumberService


def create_app():
    setup_logger(os.getenv("LOG_FILE", "logs/app.log"))

    repo = NumberRepository(os.environ["DATABASE_URL"])
    service = NumberService(repo, max_n=int(os.getenv("MAX_N", "1000000")))
    controller = NumberController(service)

    app = Flask(__name__)
    app.json.ensure_ascii = False  # чтобы русские сообщения об ошибках не превращались в \u0447...
    app.register_blueprint(controller.blueprint)
    return app


app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
