import json
import getpass
import os 

from val_api import ValorantAPI

if __name__ == "__main__":
    print("Enter user and pw or set VLR_USER and VLR_PW in env var")
    username = os.environ.get("VLR_USER") or input("your username: ")
    password = os.environ.get("VLR_PW") or getpass.getpass(prompt = "your password: ")
    region = "NA" # NA, EU, AP, KO
    client = ValorantAPI(username, password, region)

    json_match_data = client.get_match_comp_history()

    print(json.dumps(json_match_data, sort_keys=True, indent=4))