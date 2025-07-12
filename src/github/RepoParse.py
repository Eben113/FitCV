import requests
import json
import re
import pandas as pd

with open("/content/languages.json") as f:
  languages = json.load(f)

token = "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"
headers = {"Authorization": f"token ghp_{token}"}

res = requests.get("https://api.github.com/users/Eben113/repos", headers=headers)

js1 = res.json()[0]
url = js1["url"] + "/contents"
res1 = requests.get(url)
def buildLis():
  lis = [{"name": dict_["name"], "url": dict_["url"], "langURL": dict_["languages_url"]} for dict_ in res.json()]
  return lis

def scanJson(name, url, langURL):
  extensions = []
  for language in requests.get(langURL).json():
    exts = languages.get(language.title(), None)
    if exts:
      extensions.extend(exts["extensions"])
    else:
      extensions.append("."+language)
  files = requests.get(url  + "/contents").json()
  def walk(js, prefix):
    res = {}
    for branch in js:
      if branch["name"] == "README.md":
        res[prefix + "/" + "readme"] = branch["url"]
      elif branch["type"] == "file" and (("."+branch["name"].split(".")[-1]) in extensions):
        res[prefix + "/" + branch["name"]] = branch["url"]
      elif branch["type"] == "dir":
        res.update(walk(requests.get(branch["url"]).json(), prefix + "/" + branch["name"]))
    return res
  info = walk(files, name)
  return info

def buildDataset(repo_list):
  data = []
  for repo in repo_list:
    records = scanJson(repo["name"], repo["url"], repo["langURL"])
    for dir, url in records.items():
      data.append({"repo": repo["name"], "directory": dir, "url": url})
  data = pd.DataFrame(data)
  return data
