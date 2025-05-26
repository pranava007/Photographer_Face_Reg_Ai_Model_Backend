
import requests
import face_recognition
import numpy as np
import io
from PIL import Image, ImageEnhance, ImageFile
import logging

ImageFile.LOAD_TRUNCATED_IMAGES = True
logging.basicConfig(level=logging.INFO)


# def get_matched_images(selfie_url, official_photos, official_encodings, threshold=0.50):
#     try:
#         logging.info(f"📥 Total official photos: {len(official_photos)}")
#         logging.info(f"🧬 Total encodings received: {len(official_encodings)}")

#         # Load selfie image
#         response = requests.get(selfie_url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
#         response.raise_for_status()
#         selfie_img = face_recognition.load_image_file(io.BytesIO(response.content))

#         logging.info(f"📸 Selfie image shape: {selfie_img.shape}, dtype: {selfie_img.dtype}")

#         # Get selfie face encoding
#         selfie_encodings = face_recognition.face_encodings(selfie_img)
#         if not selfie_encodings:
#             logging.warning("❌ No face found in selfie image.")
#             return []

#         selfie_encoding = np.array(selfie_encodings[0])
#         logging.info(f"🧠 Selfie encoding shape: {selfie_encoding.shape}, dtype: {selfie_encoding.dtype}")
            
#         matched_images = []
        
#         # Convert official encodings to numpy array
#         official_encodings_np = np.array(official_encodings)
#         logging.info(f"🧬 Official encodings shape: {official_encodings_np.shape}, dtype: {official_encodings_np.dtype}")

       

#         # Loop through each official photo and compare
#         for i, (image_url, encoding) in enumerate(zip(official_photos, official_encodings_np)):
#             try:
#                 # Compute Euclidean distance
#                 distance = np.linalg.norm(selfie_encoding - encoding)
#                 logging.info(f"📏 Distance for image {i}: {distance}")

#                 if distance <= threshold:
#                     matched_images.append(image_url)
#                     logging.info(f"✅ Match found for image {i}: {image_url}")

#             except Exception as inner_e:
#                 logging.warning(f"⚠️ Error processing image {i}: {inner_e}")

#         logging.info(f"🎯 Total matches found: {len(matched_images)}")
#         return matched_images

#     except Exception as e:
#         logging.error(f"❌ Matching error: {e}")
#         return []




# import requests
# import face_recognition
# import numpy as np
# import io
# import logging
# from PIL import ImageFile

# ImageFile.LOAD_TRUNCATED_IMAGES = True
# logging.basicConfig(level=logging.INFO)

# def get_matched_images(selfie_url, official_photo_urls, threshold=0.50):
#     try:
#         logging.info(f"📥 Total official photo URLs: {len(official_photo_urls)}")

#         # Load and encode selfie
#         response = requests.get(selfie_url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
#         response.raise_for_status()
#         selfie_img = face_recognition.load_image_file(io.BytesIO(response.content))
#         selfie_encodings = face_recognition.face_encodings(selfie_img)

#         if not selfie_encodings:
#             logging.warning("❌ No face found in selfie image.")
#             return []

#         selfie_encoding = np.array(selfie_encodings[0])
#         matched_images = []

#         for i, image_url in enumerate(official_photo_urls):
#             try:
#                 img_resp = requests.get(image_url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
#                 img_resp.raise_for_status()
#                 official_img = face_recognition.load_image_file(io.BytesIO(img_resp.content))

#                 official_face_encodings = face_recognition.face_encodings(official_img)
#                 if not official_face_encodings:
#                     logging.warning(f"❌ No face found in official image {i}")
#                     continue

#                 # Convert all encodings to NumPy array
#                 official_face_encodings_np = np.array(official_face_encodings)

#                 # Compute distances between selfie and all faces in image
#                 distances = np.linalg.norm(official_face_encodings_np - selfie_encoding, axis=1)
#                 logging.info(f"📏 Distances for image {i}: {distances}")

#                 if np.any(distances <= threshold):
#                     matched_images.append(image_url)
#                     logging.info(f"✅ Match found for image {i}: {image_url}")

#             except Exception as err:
#                 logging.error(f"⚠️ Error processing image {i}: {err}")

#         logging.info(f"🎯 Total matches found: {len(matched_images)}")
#         return matched_images

#     except Exception as e:
#         logging.error(f"❌ Matching error: {e}")
#         return []



def get_matched_images(selfie_url, official_photos, official_encodings, threshold=0.50):
    try:
        logging.info(f"📥 Total official photo URLs: {len(official_photos)}")

        # Load and encode selfie
        response = requests.get(selfie_url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        response.raise_for_status()
        selfie_img = face_recognition.load_image_file(io.BytesIO(response.content))
        selfie_encodings = face_recognition.face_encodings(selfie_img)

        if not selfie_encodings:
            logging.warning("❌ No face found in selfie image.")
            return []

        selfie_encoding = np.array(selfie_encodings[0])
        matched_images = []

        for i, (image_url, enc_list) in enumerate(zip(official_photos, official_encodings)):
            try:
                if not enc_list:
                    logging.warning(f"❌ No encodings found for official image {i}")
                    continue

                # Convert to NumPy array if not already
                enc_np = np.array(enc_list)

                # Compute distances
                distances = np.linalg.norm(enc_np - selfie_encoding, axis=1)
                logging.info(f"📏 Distances for image {i}: {distances}")

                if np.any(distances <= threshold):
                    matched_images.append(image_url)
                    logging.info(f"✅ Match found for image {i}: {image_url}")

            except Exception as err:
                logging.error(f"⚠️ Error processing image {i}: {err}")

        logging.info(f"🎯 Total matches found: {len(matched_images)}")
        return matched_images

    except Exception as e:
        logging.error(f"❌ Matching error: {e}")
        return []
