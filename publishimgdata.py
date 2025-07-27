from google.cloud import pubsub_v1
from google.oauth2 import service_account
import base64
import time
import glob

# --- Configuration ---
project_id = "adminium-in3jn"
topic_name = "frame-data"  # Create this topic in Pub/Sub
key_path = "adminium-in3jn-2b6686badcff.json"  # Change to your actual path

# Create credentials and Publisher client
credentials = service_account.Credentials.from_service_account_file(key_path)
publisher = pubsub_v1.PublisherClient(credentials=credentials)
topic_path = publisher.topic_path(project_id, topic_name)


# Replace with your actual image capture logic
def publish_image_data():
    """Simulates capturing an image and returns its base64 encoded data."""
    image_files = glob.glob(f"*.*")

    # Optional: Filter only image extensions
    valid_exts = (".jpg", ".jpeg", ".png", ".bmp", ".gif")
    print(f"total files in the current dir: {len(image_files)}")
    for image_path in image_files:
        if image_path.lower().endswith(valid_exts):
            print("Processing:", image_path)
            try:
                with open(image_path, "rb") as image_file:
                    encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
                    data = encoded_string.encode("utf-8")
                    future = publisher.publish(topic_path, data)
                    print(f"Published message ID: {future.result()}")
                    time.sleep(10)
            except FileNotFoundError:
                print(f"Error: Dummy image not found at {image_path}. Please create one or adjust path.")
                return None
    print(f"Publishing messages to {topic_path}...")


while True:
    publish_image_data()
    print("done with sending files in current folder")
    exit(1)