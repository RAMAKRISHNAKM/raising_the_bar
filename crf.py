import os
import base64
import sys
from google.cloud import vision_v1
from google.cloud import firestore
from google.oauth2 import service_account
from google.api_core.exceptions import PermissionDenied, NotFound, GoogleAPIError

# === CONFIGURATION ===
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "adminium-in3jn-2b6686badcff.json"
PROJECT_ID = "1057762092739"
LOCATION = "europe-west4"
ENDPOINT_ID = "6865467152065888256"
BUCKET_NAME = "cloud-ai-platform-4e1fdf10-20ea-46d6-974e-95ba63665d8f"  # 🔁 Replace with your GCS bucket
KEY_PATH = "adminium-in3jn-2b6686badcff.json"

# Load credentials from file
credentials = service_account.Credentials.from_service_account_file(KEY_PATH)

# Create Vision client
vision_client = vision_v1.ImageAnnotatorClient(credentials=credentials)

# Try initializing Firestore client and check access
try:
    firestore_client = firestore.Client(credentials=credentials)
    # Dummy query to check if Firestore is active
    #print(list(firestore_client.collections()))

except (PermissionDenied, NotFound) as e:
    print("❌ Firestore is not configured or your service account lacks permission.")
    print("🔍 Details:", e)
    sys.exit(1)
except GoogleAPIError as e:
    print("❌ Could not connect to Firestore:", e)
    sys.exit(1)


def get_crowd_density_label(crowd_density_score):
    # Convert to int if it's a repeated field with a single value
    if hasattr(crowd_density_score, '__iter__') and not isinstance(crowd_density_score, (str, bytes, list)):
        crowd_density_score = list(crowd_density_score)[0]  # or sum() or len() as per logic
    elif isinstance(crowd_density_score, list):
        crowd_density_score = crowd_density_score[0]  # or sum()/len()

    crowd_density_score = int(crowd_density_score)
    if crowd_density_score <= 20:
        return "Less"
    elif 20 < crowd_density_score <= 50:
        return "Medium"
    else:
        return "Large"


def detect_faces_from_base64(encoded_string):
    client = vision_v1.ImageAnnotatorClient()

    # Decode base64 and wrap in Image object
    image = vision_v1.Image(content=base64.b64decode(encoded_string))

    response = client.face_detection(image=image, max_results=100)

    return response


# === MAIN ===
def main():

    # Example usage
    with open("IDcard.jpeg", "rb") as img_file:
        encoded_string = base64.b64encode(img_file.read()).decode("utf-8")

    response = detect_faces_from_base64(encoded_string)
    people_count = response.face_annotations
    #print(len(people_count))
    crowd_density_label = get_crowd_density_label(len(people_count))  # Placeholder logic
    print(f"people_count:{len(people_count)}, and crowd_density_score: {crowd_density_label}")
    timestamp = firestore.SERVER_TIMESTAMP

    # Store in Firestore
    doc_ref = firestore_client.collection('crowd_metrics').document()
    doc_ref.set({
        'timestamp': timestamp,
        'people_detected': people_count,
        'crowd_density_score': crowd_density_label,
    })
    #print(doc_ref)


if __name__ == "__main__":
    main()
