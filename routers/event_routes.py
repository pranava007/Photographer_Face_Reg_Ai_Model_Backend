
from flask import Blueprint
from controllers.event_controller import (
    create_event, get_photographer_events, get_event_by_id, upload_user_photo,upload_official_photos
)

from controllers.event_controller import upload_user_photo, match_user_selfie

event_bp = Blueprint("event_bp", __name__)

# Event creation and fetch
@event_bp.route("/api/event", methods=["POST"])
def create_event_route():
    return create_event()

@event_bp.route("/api/events", methods=["GET"])
def get_all_events_route():
    return get_photographer_events()

@event_bp.route("/api/events/<event_id>", methods=["GET"])
def get_event_by_id_route(event_id):
    return get_event_by_id(event_id)



@event_bp.route("/api/events/<event_id>/user-upload", methods=["POST"])
def upload_user_photo_route(event_id):
    return upload_user_photo(event_id)

@event_bp.route("/api/events/<event_id>/ai-match", methods=["POST"])
def ai_match_user_photo_route(event_id):
    return match_user_selfie(event_id)

# i add new test =========================++++++++++++++++==============================

@event_bp.route("/api/events/<event_id>/upload-official", methods=["POST"])
def upload_official_photo_route(event_id):
    return upload_official_photos(event_id)



