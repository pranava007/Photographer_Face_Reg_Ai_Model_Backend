# # # controllers/upload_controller.py

# from flask import request, jsonify
# from flask_jwt_extended import jwt_required, get_jwt, get_jwt_identity
# from database import mongo
# from bson import ObjectId

# # @jwt_required()
# # def upload_official_photos(event_id):
# #     claims = get_jwt()
# #     user_id = get_jwt_identity()

# #     if claims['role'] != 'photographer':
# #         return jsonify({"error": "Only photographers can upload photos"}), 403

# #     data = request.get_json()
# #     photo_urls = data.get("photo_urls")

# #     if not isinstance(photo_urls, list) or not photo_urls:
# #         return jsonify({"error": "photo_urls must be a non-empty list"}), 400

# #     result = mongo.db.events.update_one(
# #         {"_id": ObjectId(event_id)},
# #         {"$push": {"official_photos": {"$each": photo_urls}}}
# #     )

# #     if result.modified_count == 1:
# #         return jsonify({"message": "Photos saved successfully"}), 200
# #     return jsonify({"error": "Event not found"}), 404

# @jwt_required()
# def upload_official_photos(event_id):
#     claims = get_jwt()
#     user_id = get_jwt_identity()

#     if claims['role'] != 'photographer':
#         return jsonify({"error": "Only photographers can upload photos"}), 403

#     data = request.get_json(force=True)  # <-- use force=True for debugging

#     print("🔥 Incoming upload payload:", data)  # <-- add this line

#     photo_urls = data.get("photo_urls")

#     if not isinstance(photo_urls, list) or not photo_urls:
#         return jsonify({"error": "photo_urls must be a non-empty list"}), 400
