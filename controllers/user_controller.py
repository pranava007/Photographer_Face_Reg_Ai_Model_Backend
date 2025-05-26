from database import mongo
from models.user_model import user_schema
from flask import request, jsonify
from werkzeug.security import generate_password_hash
import datetime

def register_user():
    data = request.get_json()

    if not all(key in data for key in ("name", "email", "password", "role")):
        return jsonify({"error": "Missing fields"}), 400

    hashed_password = generate_password_hash(data['password'])

    user = {
        "name": data['name'],
        "email": data['email'],
        "password": hashed_password,
        "role": data['role'],
        "created_at": datetime.datetime.utcnow()
    }

    result = mongo.db.users.insert_one(user)
    new_user = mongo.db.users.find_one({"_id": result.inserted_id})
    return jsonify(user_schema(new_user)), 201
