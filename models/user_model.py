from bson import ObjectId

def user_schema(user):
    return {
        "_id": str(user["_id"]),
        "name": user["name"],
        "email": user["email"],
        "password": user["password"],   # This will be hashed
        "role": user["role"],            # "admin" or "photographer"
        "created_at": user.get("created_at")
    }
