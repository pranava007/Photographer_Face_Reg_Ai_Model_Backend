from bson import ObjectId

def event_schema(event):
    return {
        "_id": str(event["_id"]),
        "admin_id": str(event["admin_id"]),      # Reference to user _id
        "event_name": event["event_name"],
        "event_date": event["event_date"],
        "qr_code_url": event.get("qr_code_url", ""),
        "official_photos": event.get("official_photos", []),  # Firebase URLs
        "user_uploads": event.get("user_uploads", []),
        "created_at": event.get("created_at")
    }