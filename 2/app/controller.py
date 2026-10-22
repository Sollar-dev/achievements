from flask import Blueprint, jsonify, request

from service import DuplicateNumberError, InvalidNumberError, PreviousNumberError


class NumberController:
    def __init__(self, service):
        self.service = service
        self.blueprint = Blueprint("numbers", __name__)
        self.blueprint.add_url_rule("/increment", view_func=self.increment, methods=["POST"])

    def increment(self):
        data = request.get_json(silent=True)
        if not isinstance(data, dict):
            data = {}

        try:
            result = self.service.process(data.get("number"))
        except InvalidNumberError as e:
            return jsonify(error=str(e)), 400
        except (DuplicateNumberError, PreviousNumberError) as e:
            return jsonify(error=str(e)), 409

        return jsonify(result=result), 200
