import requests

url = "https://api.brightdata.com/datasets/v3/trigger"

headers = {
    "Authorization": "",
    "Content-Type": "application/json"
}

payload = [
    {
        "url": "https://www.instagram.com/doverstreetmarketnewyork/",
        "start_date": "",
        "end_date": "",
        "post_type": ""
    }
]

params = {
    "dataset_id": "",
    "include_errors": "true",
    "type": "discover_new",
    "discover_by": "url"
}

response = requests.post(url, headers=headers, json=payload, params=params)

print(response.status_code)
print(response.text)
