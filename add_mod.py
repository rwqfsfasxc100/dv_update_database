import os
import math
import json

from pathlib import PureWindowsPath


directory_path = PureWindowsPath(os.path.dirname(os.path.realpath(__file__))).as_posix() + "/"
mod_data_file = open(directory_path + "manifest_path_store.json", "r", encoding="utf-8")
mod_data = json.load(mod_data_file)


pld = os.environ["THIS_PAYLOAD"]
payload = json.loads(pld)

mod_id = payload.get("id","")
manifest_url = payload.get("manifest_url","")
github_url = payload.get("github_url","")
if mod_id and manifest_url and github_url:
    mod_data[mod_id]["manifest_url"] = manifest_url
    mod_data[mod_id]["github_url"] = github_url
mdrf = open(directory_path + "manifest_path_store.json", 'w', encoding="utf-8")
json.dump(mod_data, mdrf, indent="\t")