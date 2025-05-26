from flask import Blueprint, jsonify
from database import mongo

test_bp = Blueprint('test_bp', __name__)

@test_bp.route("/api/test-connection", methods=["GET"])
def test_connection():
    try:
        mongo.cx.admin.command('ping')
        return jsonify({"message": "MongoDB connection successful ✅"}), 200
    except Exception as e:
        return jsonify({"message": "MongoDB connection failed ❌", "error": str(e)}), 500
