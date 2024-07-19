# https://github.com/hiroi-sora/Umi-OCR/blob/main/docs/http/api_doc.md#/api/doc

import os
import json
import time
import requests

base_url = "http://127.0.0.1:1224"

url = "{}/api/doc/upload".format(base_url)

print("=======================================")
print("===== 1. Upload file, get task ID =====")
print("== URL:", url)

# File to be recognized
file_path = r"XXXXX.pdf"
# Task parameters
options_json = json.dumps(
    {
        "doc.extractionMode": "mixed",
    }
)
with open(file_path, "rb") as file:
    response = requests.post(url, files={"file": file}, data={"json": options_json})
response.raise_for_status()
res_data = json.loads(response.text)
if res_data["code"] == 101:
    # If code == 101, it indicates that the server did not receive the uploaded file.
    # On some Linux systems, if file_name contains non-ASCII characters, this error might occur.
    # In this case, we can specify a temp_name containing only ASCII characters to construct the upload request.

    file_name = os.path.basename(file_path)
    file_prefix, file_suffix = os.path.splitext(file_name)
    temp_name = "temp" + file_suffix
    print("[Warning] Detected file upload failure: code == 101")
    print(
        "Attempting to use temp_name",
        temp_name,
        "instead of the original file_name",
        file_name,
    )
    with open(file_path, "rb") as file:
        response = requests.post(
            url,
            # use temp_name to construct the upload request
            files={"file": (temp_name, file)},
            data={"json": options_json},
        )
    response.raise_for_status()
    res_data = json.loads(response.text)
assert res_data["code"] == 100, "Task submission failed: {}".format(res_data)

id = res_data["data"]
print("Task ID:", id)

url = "{}/api/doc/result".format(base_url)
print("===================================================")
print("===== 2. Poll task status until OCR task ends =====")
print("== URL:", url)

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
    assert res_data["code"] == 100, "Failed to get task status: {}".format(res_data)

    print(
        "    Progress: {}/{}".format(
            res_data["processed_count"], res_data["pages_count"]
        )
    )
    if res_data["data"]:
        print("{}\n========================".format(res_data["data"]))
    if res_data["is_done"]:
        state = res_data["state"]
        assert state == "success", "Task execution failed: {}".format(
            res_data["message"]
        )
        print("OCR task completed.")
        break

url = "{}/api/doc/download".format(base_url)
print("======================================================")
print("===== 3. Generate target file, get download link =====")
print("== URL:", url)

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
download_options["id"] = id
data_str = json.dumps(download_options)
response = requests.post(url, data=data_str, headers=headers)
response.raise_for_status()
res_data = json.loads(response.text)
assert res_data["code"] == 100, "Failed to get download URL: {}".format(res_data)

url = res_data["data"]
name = res_data["name"]

print("===================================")
print("===== 4. Download target file =====")
print("== URL:", url)

# Save location for downloaded files
download_dir = "./download"
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
                    "    Downloading file: {}MB | Progress: {:.2f}%".format(
                        int(downloaded_size / 1048576), progress
                    )
                )
print("Target file downloaded successfully: ", download_path)

url = "{}/api/doc/clear/{}".format(base_url, id)
print("============================")
print("===== 5. Clean up task =====")
print("== URL:", url)

response = requests.get(url)
response.raise_for_status()
res_data = json.loads(response.text)
assert res_data["code"] == 100, "Task cleanup failed: {}".format(res_data)
print("Task cleaned up successfully.")

print("======================\nProcess completed.")
