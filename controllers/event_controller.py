
import requests
import face_recognition
import numpy as np
import io
from PIL import Image, ImageEnhance, ImageFile
import logging
from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt, get_jwt_identity
from database import mongo
from models.event_model import event_schema
from bson import ObjectId
from datetime import datetime
import time
from controllers.ai_match_controller import get_matched_images
from threading import Thread
import qrcode
import os
from concurrent.futures import ThreadPoolExecutor
import cv2
from google.cloud import storage
ImageFile.LOAD_TRUNCATED_IMAGES = True
logging.basicConfig(level=logging.INFO)
import gc

# new start
def enhance_image(image_np):
    image_pil = Image.fromarray(image_np)
    image_pil = ImageEnhance.Contrast(image_pil).enhance(1.1)
    image_pil = ImageEnhance.Sharpness(image_pil).enhance(1.1)
    image_pil = ImageEnhance.Brightness(image_pil).enhance(1.05)
    return np.array(image_pil)

def upload_to_gcs(bucket_name, source_file_path, destination_blob_name):
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)
    blob.upload_from_filename(source_file_path)

    # ✅ Proper public access method for fine-grained buckets
    # blob.acl.save_predefined("publicRead")

    return blob.public_url




    
# new end

@jwt_required()
def create_event():
    start_time = time.time()
    claims = get_jwt()
    user_id = get_jwt_identity()

    if claims['role'] != 'photographer':
        return jsonify({"error": "Only photographers can create events"}), 403

    data = request.get_json()
    if not all(key in data for key in ("event_name", "event_date")):
        return jsonify({"error": "Missing fields"}), 400

    event = {
        "admin_id": ObjectId(user_id),
        "event_name": data['event_name'],
        "event_date": data['event_date'],
        "official_photos": [],
        "official_data": [],
        "failed_encodings": [],
        "qr_code_url": "",
        "created_at": datetime.utcnow()
    }

    try:
        # ✅ Insert event into DB
        result = mongo.db.events.insert_one(event)
        event_id = str(result.inserted_id)
        print(f"✅ Event inserted with ID: {event_id}")

        # ✅ Generate QR Code
        qr_data = f"{os.getenv('FRONTEND_URL')}/upload?event_id={event_id}"
        qr = qrcode.make(qr_data)
        local_path = f"static/qr_codes/{event_id}.png"
        os.makedirs(os.path.dirname(local_path), exist_ok=True)
        qr.save(local_path)
        print("✅ QR code saved locally")

        # ✅ Upload to GCS
        bucket_name = os.getenv("GCS_BUCKET")
        if not bucket_name:
            raise Exception("❌ GCS_BUCKET not set")

        gcs_url = upload_to_gcs(bucket_name, local_path, f"qr_codes/{event_id}.png")
        print("✅ QR code uploaded to GCS:", gcs_url)

        # ✅ Update MongoDB with QR URL
        mongo.db.events.update_one(
            {"_id": ObjectId(event_id)},
            {"$set": {"qr_code_url": gcs_url}}
        )
        print("✅ MongoDB updated with QR URL")

        # ✅ Return created event
        new_event = mongo.db.events.find_one({"_id": ObjectId(event_id)})
        print(f"✅ Event created in {round(time.time() - start_time, 2)} seconds")
        return jsonify(event_schema(new_event)), 201

    except Exception as e:
        print("❌ Event creation failed:", str(e))
        return jsonify({"error": "Event creation failed due to internal error."}), 500




# def compute_face_encoding(url):
#     try:
#         print("Encoding start.... : compute_face_encoding")
#         response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
#         image = face_recognition.load_image_file(io.BytesIO(response.content))

#         small_image = cv2.resize(image, (0, 0), fx=0.25, fy=0.25)

#         encodings = face_recognition.face_encodings(small_image)

#         # Convert only if it's a NumPy array
#         if encodings:
#             return [e.tolist() if hasattr(e, "tolist") else e for e in encodings]

#     except Exception as e:
#         print(f"❌ Encoding failed for {url}:", e)

#     return []


# def compute_face_encoding(url):
#     try:
#         print("🟢 Encoding start.... : compute_face_encoding")
        
#         # Step 1: Load the image from URL
#         response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
#         image = face_recognition.load_image_file(io.BytesIO(response.content))

#         # Step 2: Resize image for memory efficiency (70% of original size)
#         resized_image = cv2.resize(image, (0, 0), fx=0.7, fy=0.7)

#         # Step 3: Try CNN model for accurate detection
#         try:
#             face_locations = face_recognition.face_locations(resized_image, model="cnn")
#         except MemoryError:
#             print("⚠️ CNN model failed due to memory, falling back to HOG model.")
#             face_locations = face_recognition.face_locations(resized_image, model="hog")

#         print(f"✅ Total faces detected: {len(face_locations)}")

#         # Step 4: Encode each detected face
#         encodings = face_recognition.face_encodings(resized_image, known_face_locations=face_locations)

#         # Step 5: Convert NumPy encodings to lists (MongoDB compatible)
#         if encodings:
#             return [e.tolist() for e in encodings]

#     except Exception as e:
#         print(f"❌ Encoding failed for {url}: {e}")

#     return []



def compute_face_encoding(url):
    try:
        print("🟢 Encoding start.... : compute_face_encoding")

        # Step 1: Load image from URL
        response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        response.raise_for_status()
        image = face_recognition.load_image_file(io.BytesIO(response.content))

        # Step 2: Resize aggressively for memory efficiency (e.g., 40%)
        resized_image = cv2.resize(image, (0, 0), fx=0.4, fy=0.4)
        print("📏 Image resized for efficiency.")

        # Step 3: Free up memory before CNN
        gc.collect()

        # Step 4: Detect faces using CNN
        try:
            face_locations = face_recognition.face_locations(resized_image, model="cnn")
        except MemoryError:
            print("⚠️ CNN failed due to memory. Falling back to HOG model.")
            gc.collect()
            face_locations = face_recognition.face_locations(resized_image, model="hog")

        print(f"✅ Total faces detected: {len(face_locations)}")

        # Step 5: Encode faces
        encodings = face_recognition.face_encodings(resized_image, known_face_locations=face_locations)

        # Step 6: Return MongoDB-storable format
        if encodings:
            return [e.tolist() for e in encodings]
        else:
            print("⚠️ No encodings found.")
            return []

    except Exception as e:
        print(f"❌ Encoding failed for {url}: {e}")
        return []



def retry_failed_encodings(event_id, max_attempts=3, delay=5):
    attempt = 1

    while attempt <= max_attempts:
        print(f"♻️ Retry attempt {attempt}...")
        event = mongo.db.events.find_one({"_id": ObjectId(event_id)})

        # Fresh official_data
        official_data = event.get("official_data", [])
        already_encoded_urls = set(d["url"] for d in official_data)
        failed_before = set(event.get("failed_encodings", []))

        # Clean failed list by removing already encoded
        pending_to_retry = list(failed_before - already_encoded_urls)

        # ✅ Update MongoDB if any URLs are no longer failed
        if len(pending_to_retry) != len(failed_before):
            mongo.db.events.update_one(
                {"_id": ObjectId(event_id)},
                {"$set": {"failed_encodings": pending_to_retry}}
            )
            print(f"🧹 Cleaned failed_encodings list — Pending: {len(pending_to_retry)}")

        if not pending_to_retry:
            print("🎉 All images encoded successfully. Retry not needed.")
            return

        successful_retry = []
        still_failed = []

        for url in pending_to_retry: 
          encoding = compute_face_encoding(url)
          if encoding:
                successful_retry.append({"url": url, "encoding": encoding[0]})
                print("✅ Encoding pushed to MongoDB")
          else:
                still_failed.append(url)

        update_ops = {}
        if successful_retry:
            update_ops["$push"] = {"official_data": {"$each": successful_retry}}
        update_ops["$set"] = {"failed_encodings": still_failed}

        mongo.db.events.update_one({"_id": ObjectId(event_id)}, update_ops)

        print(f"✅ Retry {attempt} complete — Recovered: {len(successful_retry)}, Remaining Failed: {len(still_failed)}")

        if not still_failed:
            print("🎉 All retries successful. Exiting loop.")
            return

        time.sleep(delay)
        attempt += 1

    print("❌ Max retry attempts reached. Some images still unencoded.")




def encode_official_photos_internal(event_id):
    
    try:
        print("Encoding start.... : encode_official_photos_internal")
        
        event = mongo.db.events.find_one({"_id": ObjectId(event_id)})
        if not event:
            logging.error("❌ Event not found.")
            return
        photo_urls = event.get("official_photos", [])
        already_encoded_urls = [d["url"] for d in event.get("official_data", [])]
        failed_before = set(event.get("failed_encodings", []))

        # Only encode new or previously failed URLs
        to_process = [url for url in photo_urls if url not in already_encoded_urls or url in failed_before]

        new_data = []
        still_failed = []

        for url in to_process:
            encodings = compute_face_encoding(url)  # returns list of lists
            print("encodings",encodings)
            if encodings and isinstance(encodings, list):
                new_data.append({"url": url, "encoding": encodings})
                print("✅ Encoding pushed to MongoDB")
            else:
                still_failed.append(url)

        update_ops = {}
        if new_data:
            update_ops["$push"] = {"official_data": {"$each": new_data}}
        update_ops["$set"] = {"failed_encodings": still_failed}

        mongo.db.events.update_one({"_id": ObjectId(event_id)}, update_ops)

        print(f"✅ Encoded: {len(new_data)}, ❌ Still failed: {len(still_failed)}")

        # Retry logic if failures remain
        if still_failed:
            print("🔁 Retrying failed encodings after short delay...")
            # Thread(target=retry_failed_encodings, args=(event_id, 3, 5)).start()
            retry_failed_encodings(event_id,2,5)

    except Exception as e:
        print("❌ Internal encoding error:", e)


# def trigger_encoding_async(event_id):
#     Thread(target=encode_official_photos_internal, args=(event_id,)).start()



@jwt_required()
def upload_official_photos(event_id):
    try:
        start_time = time.time()
        data = request.get_json()
        photo_urls = data.get("photo_urls")

        if not isinstance(photo_urls, list) or not photo_urls:
            return jsonify({"error": "photo_urls must be a non-empty list"}), 400

        mongo.db.events.update_one(
            {"_id": ObjectId(event_id)},
            {"$push": {"official_photos": {"$each": photo_urls}}}
        )

        print(f"✅ Upload completed in {round(time.time() - start_time, 2)} seconds")
        # trigger_encoding_async(event_id)
        encode_official_photos_internal(event_id)

        return jsonify({"message": "Photos uploaded. Encoding will process in background."}), 200

    except Exception as e:
        print("❌ Upload error:", e)
        return jsonify({"error": "Upload failed"}), 500


# # impge upload and encode Sprate Logic ===============++++++++++++=============== END


@jwt_required()
def get_photographer_events():
    user_id = get_jwt_identity()
    claims = get_jwt()

    if claims['role'] != 'photographer':
        return jsonify({"error": "Only photographers can access their events"}), 403

    events = mongo.db.events.find({"admin_id": ObjectId(user_id)})
    result = [event_schema(e) for e in events]
    return jsonify(result), 200


def get_event_by_id(event_id):
    try:
        event = mongo.db.events.find_one({"_id": ObjectId(event_id)})
        if not event:
            return jsonify({"error": "Event not found"}), 404
        return jsonify(event_schema(event)), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    

def upload_user_photo(event_id):    
    data = request.get_json()
    selfie_url = data.get("selfie_url")
    name = data.get("name")
    number = data.get("number")

    # Get event and official images/encodings
    event = mongo.db.events.find_one({"_id": ObjectId(event_id)})
    official_data = event.get("official_data", [])

    official_urls = [d["url"] for d in official_data]
    official_encodings = [d["encoding"] for d in official_data]

    # Run AI matching
    matched_urls = get_matched_images(selfie_url, official_urls, official_encodings)

    # Save to DB
    mongo.db.events.update_one(
        {"_id": ObjectId(event_id)},
        {
            "$push": {
                "user_uploads": {
                    "name": name,
                    "number": number,
                    "selfie_url": selfie_url,
                    "matched_photos": matched_urls,
                    "uploaded_at": datetime.utcnow()
                }
            }
        }
    )
    return jsonify({"message": "Uploaded", "matches": matched_urls})


def match_user_selfie(event_id):
    try:
        data = request.get_json()
        selfie_url = data.get("selfie_url")

        # Get event
        event = mongo.db.events.find_one({"_id": ObjectId(event_id)})
        if not event:
            return jsonify({"error": "Event not found"}), 404

        # Extract official data
        official_data = event.get("official_data", [])
        created_at = event.get("created_at")  # ⬅️ Get created_at field

        official_photos = []
        official_encodings = []

        for item in official_data:
            if item.get("url") and item.get("encoding"):
                official_photos.append(item["url"])
                official_encodings.append(item["encoding"])

        # Match with AI
        matched_urls = get_matched_images(selfie_url, official_photos, official_encodings)

        # Update DB
        mongo.db.events.update_one(
            {
                "_id": ObjectId(event_id),
                "user_uploads.selfie_url": selfie_url
            },
            {
                "$set": {
                    "user_uploads.$.matched_photos": matched_urls
                }
            }
        )

        return jsonify({
            "matches": matched_urls,
            "created_at": str(created_at)  # ⬅️ Include created_at in response
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500



# def match_user_selfie(event_id):
#     try:
#         data = request.get_json()
#         selfie_url = data["selfie_url"]

#         event = mongo.db.events.find_one({"_id": ObjectId(event_id)})
#         official_data = event.get("official_data", [])

#         # official_photos = [d["url"] for d in official_data]
#         # official_encodings = [d["encoding"] for d in official_data]

#         # Separate lists
#         official_photos = []
#         official_encodings = []

#         for item in official_data:
#             url = item.get("url")
#             encoding = item.get("encoding")

#             if url:
#                 official_photos.append(url)
#             if encoding:
#                 official_encodings.append(encoding)



#         matched_urls = get_matched_images(selfie_url, official_photos,official_encodings)

#         mongo.db.events.update_one(
#             {
#                 "_id": ObjectId(event_id),
#                 "user_uploads.selfie_url": selfie_url
#             },
#             {
#                 "$set": {
#                     "user_uploads.$.matched_photos": matched_urls
#                 }
#             }
#         )

#         return jsonify({"matches": matched_urls})
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500
