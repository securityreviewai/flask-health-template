from flask import Blueprint, jsonify

bp = Blueprint("main", __name__)


@bp.get("/health")
def health() -> tuple:
    return jsonify({"status": "ok"}), 200


@bp.get("/api/patients")
def list_patients() -> tuple:
    return jsonify({"patients": []}), 200
