import os
import sys
import zipfile

import requests
from bs4 import BeautifulSoup

# load previous version
if not os.path.exists("downloader.log"):
    with open("downloader.log", "w") as f:
        f.write("")
with open("downloader.log", "r") as f:
    version = f.read()

# get latest version
print("Checking for updates...")
url = "https://sangchoo1201.github.io/"
response = requests.get(url)
if response.status_code != 200:
    print("Failed to get latest version")
    input("Press Enter to exit...")
    sys.exit()

data = BeautifulSoup(response.text, "html.parser")

# check if update is needed
latest_version = data.find("p", {"id": "version"}).text
if version == latest_version:
    print("Already up-to-date")
    input("Press Enter to exit...")
    sys.exit()

# get download url
print("Downloading ZIP...")
try:
    url = "https://sangchoo1201.github.io/" + data.find("a")["href"]
except Exception as e:
    print("Failed to get download url")
    print(f"error: {e}")
    input("Press Enter to exit...")
    sys.exit()

# download zip file
response = requests.get(url)
with open("temp.zip", "wb") as f:
    f.write(response.content)

# extract zip file
print("Extracting ZIP...")
if not os.path.exists("taiji_maker"):
    os.mkdir("taiji_maker")

taiji_maker_zip = zipfile.ZipFile("temp.zip")
taiji_maker_zip.extractall(f"{os.getcwd()}/taiji_maker")

# delete zip file
print("Deleting ZIP...")
taiji_maker_zip.close()
os.remove("temp.zip")

# save latest version
with open("downloader.log", "w") as f:
    f.write(latest_version)

print("Update complete")
input("Press Enter to exit...")
