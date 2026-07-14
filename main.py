import requests
import os
import math
import json

from pathlib import PureWindowsPath

try:
    access_token = os.environ["TOKEN_SECRET"]
except KeyError:
    access_token = "Token not available!"


page_size = 100
def fetch_api(url,token):
    headers = {
        "Authorization": f"token {token}",
    }
    response = requests.get(url,headers)
    if response.status_code == 200:
        updated_repo_data = response.json()
        return updated_repo_data
    else:
        return None

def fetch_topic_page(page_no,token):
    headers = {
        "Authorization": f"token {token}",
    }
    url = 'https://api.github.com/search/repositories?q=topic:delta-v-rings-of-saturn&per_page=%s&page=%s' % (page_size,page_no)
    print(url)
    response = requests.get(url,headers)
    if response.status_code == 200:
        updated_repo_data = response.json()
        return updated_repo_data
    else:
        return None

def checkIfAcceptable(n):
    if n["draft"]:
        return False
    else:
        return True

def download_file(url,path):
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)

directory_path = PureWindowsPath(os.path.dirname(os.path.realpath(__file__))).as_posix() + "/"

topic_path = directory_path + "topic_store/"
zip_path = directory_path + "zip_store/"
if not os.path.isdir(topic_path):
    os.mkdir(topic_path)
if not os.path.isdir(zip_path):
    os.mkdir(zip_path)
print("dir: " + directory_path)

current_page = 1
data = fetch_topic_page(current_page,access_token)


datafile = open(topic_path + 'topic_page_%s.json' % current_page, 'w', encoding="utf-8")
json.dump(data, datafile, indent="\t")

total_entries = data.get("total_count",0)

page_max = math.ceil(total_entries / page_size)

while (current_page < page_max):
    current_page += 1
    this_data = fetch_topic_page(current_page,access_token)
    df = open(topic_path + 'topic_page_%s.json' % current_page, 'w', encoding="utf-8")
    json.dump(this_data, df, indent="\t")

mod_data_file = open(directory_path + "manifest_path_store.json", "r", encoding="utf-8")
mod_data = json.load(mod_data_file)

for mod_id in mod_data:
    manifestpath = mod_data[mod_id]["manifest_path"]
    print("fetching %s @ %s" % (mod_id,manifestpath)
    response = requests.get(manifestpath)
    if response.status_code == 200:
        needs_update = False
        ver_string_format = "%s.%s.%s"
        newver_major = 0
        newver_minor = 0
        newver_bugfix = 0
        curver_major = mod_data[mod_id]["major"]
        curver_minor = mod_data[mod_id]["minor"]
        curver_bugfix = mod_data[mod_id]["bugfix"]
        oldver = ver_string_format % (curver_major,curver_minor,curver_bugfix)
        capture_version = False
        
        current_zip_path = zip_path + mod_id + "/"
        if not os.path.isdir(current_zip_path):
            print("mod zip store doesn't exist, ensuring update: " + current_zip_path)
            needs_update = True
        
        if not needs_update:
            for ln in str(response.text).split("\n"):
                line = ln.strip()
                if line.startswith("[",0,1) and line.endswith("]"):
                    capture_version = line == "[version]"
                if capture_version:
                    line_split = line.split("=")
                    if len(line_split) > 1:
                        match line_split[0]:
                            case "version_major":
                                newver_major = int(line_split[1])
                            case "version_minor":
                                newver_minor = int(line_split[1])
                            case "version_bugfix":
                                newver_bugfix = int(line_split[1])
            if newver_major > curver_major:
                needs_update = True
            elif newver_minor > curver_minor:
                needs_update = True
            elif newver_bugfix > curver_bugfix:
                needs_update = True
            if needs_update:
                print("Out of date, fetching new version")
        if needs_update:
            mod_data[mod_id]["major"] = newver_major
            mod_data[mod_id]["minor"] = newver_minor
            mod_data[mod_id]["bugfix"] = newver_bugfix
            
            newver = ver_string_format % (newver_major,newver_minor,newver_bugfix)
            github_url = mod_data[mod_id]["github_url"]
            if github_url.endswith("/"):
                github_url = github_url[:-1]
            if not github_url.endswith("/releases"):
                github_url = github_url + "/releases"
            github_url = "https://api.github.com/repos/" + github_url.split("https://github.com/")[1]
            print("updating %s [v%s] from %s" % (manifestpath,newver,github_url))
            release_data = fetch_api(github_url,access_token)
            if release_data != None:
                print("fetched mod info")
                download_url = ""
                for n in release_data:
                    if checkIfAcceptable(n):
                        for asset in n["assets"]:
                            download_url = asset["browser_download_url"]
                            break
                        if download_url:
                            break
                if download_url:
                    this_zip_path = zip_path + mod_id + "/"
                    if not os.path.isdir(this_zip_path):
                        os.mkdir(this_zip_path)
                    this_zip_path = this_zip_path + newver + "/"
                    if not os.path.isdir(this_zip_path):
                        os.mkdir(this_zip_path)
                    zipname = download_url.split("/")[-1]
                    mod_data[mod_id]["file_name"] = zipname
                    zip_file = this_zip_path + zipname
                    print("downloading mod zip from %s to %s " % (download_url,zip_file))
                    download_file(download_url,zip_file)
            else:
                print("failed to fetch mod info")
    else:
        print("failed to fetch " + manifestpath)
mdrf = open(directory_path + "manifest_path_store.json", 'w', encoding="utf-8")
json.dump(mod_data, mdrf, indent="\t")