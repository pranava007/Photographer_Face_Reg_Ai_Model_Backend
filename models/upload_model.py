from bson import ObjectId

def upload_schema(upload):
    return {
        "_id": str(upload["_id"]),
        "event_id": str(upload["event_id"]),           # Which event this upload belongs
        "user_selfie_url": upload["user_selfie_url"],   # Firebase URL of selfie
        "matched_photos": upload.get("matched_photos", []),  # Firebase URLs
        "uploaded_at": upload.get("uploaded_at")
    }