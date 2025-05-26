from flask import request, jsonify
from database import mongo
from werkzeug.security import check_password_hash
from flask_jwt_extended import create_access_token
from bson import ObjectId

def login_user():
    data = request.get_json()

    if not data.get('email') or not data.get('password'):
        return jsonify({"error": "Email and Password are required"}), 400

    user = mongo.db.users.find_one({"email": data['email']})

    if not user:
        return jsonify({"error": "Invalid email or password"}), 401

    if not check_password_hash(user['password'], data['password']):
        return jsonify({"error": "Invalid email or password"}), 401

    # access_token = create_access_token(
    #     identity=str(user['_id']),
    #     additional_claims={"role": user['role']}
    # )

    # return jsonify({
    #     "access_token": access_token,
    #     "name":user['name'],
    #     "email":user['emil'],
    #     "role": user['role']
    # }), 200
    access_token = create_access_token(
    identity=str(user['_id']),
    additional_claims={"role": user['role']}
    )

    return jsonify({
        "access_token": access_token,
        "name": user['name'],
        "email": user['email'],  # ✅ corrected spelling
        "role": user['role']
    }), 200
