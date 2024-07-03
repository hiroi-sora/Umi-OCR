import os
import json
import time
import requests

base_url = "http://127.0.0.1:1224"
# File to be recognized
file_path = r"XXXXX.pdf"
# Task parameters
mission_options = {
    "doc.extractionMode": "fullPage",
}
# Save location for downloaded files
download_dir = "./download"
# Download file parameters
download_options = {
    "file_types": [
        "txt",
        "txtPlain",
        "jsonl",
        "csv",
        "pdfLayered",
        "pdfOneLayer",
    ],
    "ingore_blank": False,  # Do not ignore blank pages
}

# =========================================================

print("=======================================")
print("===== 1. Upload file, get task ID =====")
url = f"{base_url}/api/doc/upload"
with open(file_path, "rb") as file:
    response = requests.post(
        url, files={"file": file}, data={"json": json.dumps(mission_options)}
    )
response.raise_for_status()
res_data = json.loads(response.text)
assert res_data["code"] == 100, f"Task submission failed: {res_data}"

id = res_data["data"]
print("Task ID:", id)

print("===================================================")
print("===== 2. Poll task status until OCR task ends =====")
url = f"{base_url}/api/doc/result"
headers = {"Content-Type": "application/json"}
data_str = json.dumps(
    {
        "id": id,
        "is_data": True,
        "format": "text",
        "is_unread": True,
    }
)
while True:
    time.sleep(1)
    response = requests.post(url, data=data_str, headers=headers)
    response.raise_for_status()
    res_data = json.loads(response.text)
    assert res_data["code"] == 100, f"Failed to get task status: {res_data}"

    print(f'    Progress: {res_data["processed_count"]}/{res_data["pages_count"]}')
    if res_data["data"]:
        print(f'{res_data["data"]}\n========================')
    if res_data["is_done"]:
        state = res_data["state"]
        assert state == "success", f"Task execution failed: {res_data['message']}"
        print(f"OCR task completed.")
        break

print("======================================================")
print("===== 3. Generate target file, get download link =====")
url = f"{base_url}/api/doc/download"
download_options["id"] = id
data_str = json.dumps(download_options)
response = requests.post(url, data=data_str, headers=headers)
response.raise_for_status()
res_data = json.loads(response.text)
assert res_data["code"] == 100, f"Failed to get download URL: {res_data}"

url = res_data["data"]
name = res_data["name"]

print("===================================")
print("===== 4. Download target file =====")
print(f"URL: {url}")
if not os.path.exists(download_dir):
    os.makedirs(download_dir)
download_path = os.path.join(download_dir, name)
response = requests.get(url, stream=True)
response.raise_for_status()
# Download file size
total_size = int(response.headers.get("content-length", 0))
downloaded_size = 0
log_size = 10485760  # Print progress every 10MB

with open(download_path, "wb") as file:
    for chunk in response.iter_content(chunk_size=8192):
        if chunk:
            file.write(chunk)
            downloaded_size += len(chunk)
            if downloaded_size >= log_size:
                log_size = downloaded_size + 10485760
                progress = (downloaded_size / total_size) * 100
                print(
                    f"    Downloading file: {int(downloaded_size/1048576)}MB | Progress: {progress:.2f}%"
                )
print(f"Target file downloaded successfully: {download_path}")

print("============================")
print("===== 5. Clean up task =====")
url = f"{base_url}/api/doc/clear/{id}"
response = requests.get(url)
response.raise_for_status()
res_data = json.loads(response.text)
assert res_data["code"] == 100, f"Task cleanup failed: {res_data}"
print("Task cleaned up successfully.")

print("======================\nProcess completed.")
