import os
import requests
from dotenv import load_dotenv

load_dotenv()

TENANT_ID = os.getenv("POWERBI_TENANT_ID")
CLIENT_ID = os.getenv("POWERBI_CLIENT_ID")
CLIENT_SECRET = os.getenv("POWERBI_CLIENT_SECRET")
WORKSPACE_ID = os.getenv("POWERBI_WORKSPACE_ID")
REPORT_ID = os.getenv("POWERBI_REPORT_ID")


def get_access_token():
    url = f"https://login.microsoftonline.com/{TENANT_ID}/oauth2/v2.0/token"

    payload = {
        "grant_type": "client_credentials",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "scope": "https://analysis.windows.net/powerbi/api/.default",
    }

    response = requests.post(url, data=payload)

    if response.status_code != 200:
        print("Status Code:", response.status_code)
        print("Response:", response.text)
        raise Exception(response.text)

    return response.json()["access_token"]  


def get_embed_details():
    token = get_access_token()

    headers = {
        "Authorization": f"Bearer {token}"
    }

    # Get report details
    url = (
        f"https://api.powerbi.com/v1.0/myorg/groups/"
        f"{WORKSPACE_ID}/reports/{REPORT_ID}"
    )

    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        print("Status Code:", response.status_code)
        print("Response:", response.text)
        raise Exception(response.text)

    report = response.json()

    # Generate Embed Token
    embed_token_url = (
        f"https://api.powerbi.com/v1.0/myorg/groups/"
        f"{WORKSPACE_ID}/reports/{REPORT_ID}/GenerateToken"
    )

    payload = {
        "accessLevel": "View"
    }

    embed_response = requests.post(
        embed_token_url,
        headers=headers,
        json=payload
    )

    if embed_response.status_code != 200:
        print("Generate Token Error:", embed_response.text)
        raise Exception(embed_response.text)

    embed_token = embed_response.json()["token"]

    return {
        "reportId": REPORT_ID,
        "embedUrl": report["embedUrl"],
        "accessToken": embed_token
    }