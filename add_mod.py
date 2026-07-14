import os
import math
import json

from pathlib import PureWindowsPath


directory_path = PureWindowsPath(os.path.dirname(os.path.realpath(__file__))).as_posix() + "/"
mod_data_file = open(directory_path + "manifest_path_store.json", "r", encoding="utf-8")
mod_data = json.load(mod_data_file)


pld = os.environ["THIS_PAYLOAD"]
payload = json.loads(pld)
print("Payload: " + payload)


