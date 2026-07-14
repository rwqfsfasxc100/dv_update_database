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

fetcher_store = directory_path + "github_fetcher_store/"
fetcher_icon_path = fetcher_store + "icons/"
fetcher_zip_path = fetcher_store + "zips/"
if not os.path.isdir(topic_path):
    os.mkdir(topic_path)
if not os.path.isdir(zip_path):
    os.mkdir(zip_path)
if not os.path.isdir(fetcher_store):
    os.mkdir(fetcher_store)
if not os.path.isdir(fetcher_icon_path):
    os.mkdir(fetcher_icon_path)
if not os.path.isdir(fetcher_zip_path):
    os.mkdir(fetcher_zip_path)
print("dir: " + directory_path)

compiled_topic_file = fetcher_store + 'compiled_topic_store.json'
if not os.path.isfile(compiled_topic_file):
    jds = open(compiled_topic_file, 'w', encoding="utf-8")
    json.dump(json.loads("{}"), jds, indent="\t")


def topic_format(item, current_page):
    topic_filepath = topic_path + 'topic_page_%s.json' % current_page
    details_filepath = "https://raw.githubusercontent.com/%s/refs/heads/%s/MOD_DETAILS.txt"
    topic_data_file = open(compiled_topic_file, "r", encoding="utf-8")
    topic_data = json.load(topic_data_file)
    for DATA in item["items"]:
        branch = DATA.get("default_branch")
        pathName = DATA.get("full_name")
        path = "https://raw.githubusercontent.com/%s/refs/heads/%s/MOD_DETAILS.txt" % (pathName,branch)
        
        owner = DATA.get("owner")
        avatar_url = owner.get("avatar_url","")
        username = owner.get("login","")
        response = requests.get(path)
        if response.status_code == 200:
            details = response.text
            formatted_details = get_mod_details_custom_icon(details,avatar_url)
            
            latest_release_path = DATA.get("html_url") + "/releases/latest"
            rs = requests.get(latest_release_path)
            
            if rs.status_code == 200:
                rd = rs.text
                specificLine = False
                for ln in str(rd).split("\n"):
                    line = ln.strip()
                    if line.startswith("<title>",0,7):
                        specificLine = True
                        break
                
                release_url = DATA.get("html_url") + "/latest"
                
                entry = DATA.get("full_name")
                release_download = "https://api.github.com/repos/%s/releases" % (entry)
                
                fetch_zip = requests.get(release_download)
                
                if fetch_zip.status_code == 200:
                    release_fetch = json.loads(fetch_zip.text)[0]["assets"][0]
                    
                    zpfn = release_fetch.get("name","temp.zip")
                    custom_filename = formatted_details["header_data"].get("MOD_ZIP_NAME","")
                    if custom_filename:
                        zpfn = custom_filename
                    
                    this_mod_id = formatted_details["header_data"].get("MOD_ID","")
                    this_username = formatted_details["header_data"].get("AUTHOR",username)
                    formatted_details["header_data"]["AUTHOR"] = this_username
                    this_zip_url = release_fetch.get("browser_download_url")
                    specific_zip_filepath = fetcher_zip_path + this_mod_id + "/"
                    if not os.path.isdir(specific_zip_filepath):
                        os.mkdir(specific_zip_filepath)
                    
                    download_file(this_zip_url,specific_zip_filepath + zpfn)
                    
                    icon_url = formatted_details["header_data"].get("MOD_ICON",avatar_url)
                    if not icon_url:
                        icon_url = avatar_url
                    if this_mod_id:
                        if not this_mod_id in topic_data:
                            topic_data[this_mod_id] = {}
                        
                        icon_filepath = fetcher_icon_path + this_mod_id + ".png"
                        
                        
                        if icon_url:
                            download_file(icon_url,icon_filepath)
                        else:
                            icon_filepath = ""
                            print("ERROR: MISSING ICON FOR " + this_mod_id)
                        
                        
                        topic_data[this_mod_id]["formatted"] = formatted_details
                        if icon_url:
                            topic_data[this_mod_id]["icon_path"] = "https://raw.githubusercontent.com/rwqfsfasxc100/dv_update_database/refs/heads/main/github_fetcher_store/icons/" + this_mod_id + ".png"
                        else:
                            topic_data[this_mod_id]["icon_path"] = ""
                        topic_data[this_mod_id]["zip_filename"] = "https://raw.githubusercontent.com/rwqfsfasxc100/dv_update_database/refs/heads/main/github_fetcher_store/zips/" + this_mod_id + "/" + zpfn
                    
                    
                    
                    
                else:
                    print("MISSING MOD ID: " + path)
    jgt = open(compiled_topic_file, 'w', encoding="utf-8")
    json.dump(topic_data, jgt, indent="\t")

def get_mod_details_custom_icon(text,avatar_url):
    dta = json.loads('{"header_data":{},"readme":""}')
    description = ""
    for ln in str(text).split("\n"):
        line = ln.strip()
        if line.startswith(";",0,1):
            line = line[1:]
            lsplit = line.split("|")
            if len(lsplit) == 2:
                dta["header_data"][lsplit[0]] = lsplit[1]
        else:
            description = description + line + "\n"
    dta["readme"] = description
    return dta
    

current_page = 1
data = fetch_topic_page(current_page,access_token)
topic_format(data, current_page)

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
    manifestpath = mod_data[mod_id]["manifest_url"]
    print("fetching %s @ %s" % (mod_id,manifestpath))
    response = requests.get(manifestpath)
    if response.status_code == 200:
        needs_update = False
        ver_string_format = "%s.%s.%s"
        newver_major = 0
        newver_minor = 0
        newver_bugfix = 0
        curver_major = mod_data[mod_id].get("major",0)
        curver_minor = mod_data[mod_id].get("minor",0)
        curver_bugfix = mod_data[mod_id].get("bugfix",0)
        oldver = ver_string_format % (curver_major,curver_minor,curver_bugfix)
        capture_version = False
        
        current_zip_path = zip_path + mod_id + "/"
        if not os.path.isdir(current_zip_path):
            print("mod zip store doesn't exist, ensuring update: " + current_zip_path)
            needs_update = True
        curver_zip_path = current_zip_path + oldver + "/"
        if not os.path.isdir(curver_zip_path):
            print("mod version store doesn't exist, ensuring update: " + curver_zip_path)
            needs_update = True
        if not os.path.isfile(curver_zip_path + mod_data[mod_id].get("file_name","file.zip")):
            print("mod version file doesn't exist, ensuring update: " + curver_zip_path)
            needs_update = True
        
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
        if not needs_update:
            if newver_major > curver_major:
                needs_update = True
            elif newver_minor > curver_minor:
                needs_update = True
            elif newver_bugfix > curver_bugfix:
                needs_update = True
        if needs_update:
            print("Out of date, fetching new version")
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