import json
import os
from dotenv import load_dotenv

load_dotenv()


# Load credentials from JSON file
def load_credentials():
    if not os.path.exists("credentials.json"):
        return {}
    with open("credentials.json", "r") as file:
        return json.load(file)

# Save credentials to JSON file
def save_credentials(credentials):
    with open("credentials.json", "w") as file:
        json.dump(credentials, file, indent=4)