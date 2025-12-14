import requests
import time

url = "http://localhost:8000/download"

payload = {
    "url": "https://www.facebook.com/share/v/1FUnpGDyAH/"
}

headers = {
    "Content-Type": "application/json"
}

s_time = time.time()

for i in range(1, 7):
    response = requests.post(url, json=payload, headers=headers)

    print(f"Request {i}")
    print("Status Code:", response.status_code)

    try:
        print("Response:", response.json())
    except Exception:
        print("Response Text:", response.text)

    print("-" * 50)

    time.sleep(0.2)  # small delay to avoid accidental batching

print(time.time() - s_time)