import os
import sys
import zipfile

import requests
from bs4 import BeautifulSoup
from lxml import etree

# load previous version
if not os.path.exists("downloader.log"):
    with open("downloader.log", "w") as f:
        f.write("")
with open("downloader.log", "r") as f:
    version = f.read()

# get latest version
print("Checking for updates...")
url = "https://github.com/sangchoo1201/taiji_maker/releases/latest"
response = requests.get(url)
if response.status_code != 200:
    print("Failed to get latest version")
    input("Press Enter to exit...")
    sys.exit()

data = BeautifulSoup(response.text, "html.parser")
xpath = etree.HTML(str(data))

# check if update is needed
path = '//*[@id="repo-content-pjax-container"]/div/div/div/div[1]/div[2]/div[1]/h1'
latest_version = xpath.xpath(path)[0].text
if version == latest_version:
    print("Already up-to-date")
    input("Press Enter to exit...")
    sys.exit()

# get download url
print("Downloading ZIP...")
for i in (1, 2):
    path = f'//*[@id="repo-content-pjax-container"]/div/div/div/div[2]/div[1]/details/div/div/ul/li[{i}]/div[1]/a'
    url = "https://github.com/" + xpath.xpath(path)[0].attrib["href"]
    if url.endswith("taiji_maker.zip"):
        break
else:
    print("Failed to get download url")
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
