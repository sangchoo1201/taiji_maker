import os
import sys

import requests
import zipfile


# load previous version
if not os.path.exists("updater.log"):
    with open("updater.log", "w") as f:
        f.write("")
    version = ""
else:
    with open("updater.log", "r") as f:
        version = f.read()

# get latest version
print("Checking for updates...")
url = "https://api.github.com/repos/sangchoo1201/taiji_maker/releases/latest"
response = requests.get(url)
data = response.json()

# check if update is needed
if version == data["name"]:
    print("Already up-to-date")
    sys.exit()

# get download url
print("Downloading ZIP...")
url = next((asset["browser_download_url"] for asset in data["assets"] if asset["name"] == "taiji_maker.zip"), "")

if not url:
    print("No zip file found")
    sys.exit()

# download zip file
response = requests.get(url)
with open("temp.zip", "wb") as f:
    f.write(response.content)


# make a backup of main.exe
print("Backing up main.exe...")
with open("main.exe", "rb") as f:
    main = f.read()

with open("backup.exe", "wb") as f:
    f.write(main)

# delete current main.exe
print("Deleting main.exe...")
os.remove("main.exe")

# extract zip file
print("Extracting ZIP...")
taiji_maker_zip = zipfile.ZipFile("temp.zip")
taiji_maker_zip.extract("main.exe")

# delete zip file
print("Deleting ZIP...")
taiji_maker_zip.close()
os.remove("temp.zip")

# save latest version
with open("updater.log", "w") as f:
    f.write(data["name"])

print("Update complete")
