import requests
import os

try:
  access_token = os.environ["TOKEN_SECRET"]
except KeyError:
  access_token = "Token not available!"


def fetch_api(url,token):
  headers = {
    "Authorization": f"token {token}",
  }
  
  response = requests.fetch(url,headers)
  if response.status_code == 200:
    updated_repo_data = response.json()
    return updated_repo_data
else:
    return None

def fetch_topic_page(page_no,token):
  headers = {
    "Authorization": f"token {token}",
  }
  
  response = requests.fetch('https://api.github.com/search/repositories?q=topic:delta-v-rings-of-saturn&per_page=100&page=%s' % page_no,headers)
  if response.status_code == 200:
    updated_repo_data = response.json()
    return updated_repo_data
else:
    return None
