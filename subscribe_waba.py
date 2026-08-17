import requests
import os
from dotenv import load_dotenv

load_dotenv()

ACCESS_TOKEN = os.getenv("META_ACCESS_TOKEN")
WABA_ID = "1663763854945288"

url = f"https://graph.facebook.com/v21.0/{WABA_ID}/subscribed_apps"
headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}

response = requests.post(url, headers=headers)

print("Status code:", response.status_code)
print("Response body:", response.text)