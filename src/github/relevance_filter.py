import requests
from datasets import load_dataset, Dataset
import pandas as pd
import base64
token = "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"
headers = {"Authorization": f"token ghp_{token}"}

def parse_repo(df, tokenizer, gen_pipeline, role):
  def return_role_prompts(role, task, files, tokenize=False):
    task_prompt = {"describe" :  "return a one paragraph project description that shows how this project displays skills that make me good for this job role or posting:", "skill" : "return a list of skills that were showcased in this project and that recruiters look for when looking people for this job role or posting in this format 1. :"}
    assistant_prompt = {"describe":"Suggested project title: ", "skill":"1. "}
    prompts =  tokenizer.apply_chat_template([{"role":"system", "content":"You are a CV coach with expertise in editing CVs for people who work in tech"},
                                                            {"role":"user", "content":"These are some (or all) of the files for a particular project I worked on (written in the format Directory:File_1_directory||Content:File_1_content, Directory:File_2_directory||Content:File_2_content,...):"+files+ task_prompt[task] +role+" and would be a good thing to put on my CV"},
                                                            {"role":"assistant", "content":assistant_prompt[task]}], tokenize = tokenize, continue_final_message=True)
    return prompts


  def chunk(text, max_length):
    chunks = []
    tokens = tokenizer.encode(text)
    current = 0
    for i in range(len(tokens)//max_length):
      chunks.append(tokenizer.decode(tokens[current : current+max_length]))
      current += max_length
    chunks.append(tokenizer.decode(tokens[current:]))
    return chunks


  def collate(df, role):
    projects = set(df.repo)
    res = []
    for project in projects:
      current_files = ""
      skills, describe = [], []
      for i, row in df[df["repo"] == project].iterrows():
        if len(return_role_prompts(role, "skill", current_files, True)) >= 7000:
          skills.extend([return_role_prompts(role, "skill", string, False) for string in chunk(current_files, 2500)])
          describe.extend([return_role_prompts(role, "describe", string, False) for string in chunk(current_files, 2500)])
          current_files = ""
        doc = requests.get(row["url"], headers=headers).json()
        doc = base64.b64decode(doc["content"])
        new = "Directory:{}||Content:{}".format(row["directory"], doc.decode("utf-8"))
        if len(return_role_prompts(role, "skill", current_files+new, True)) <= 2500:
          current_files += new
        else:
          skills.append(return_role_prompts(role, "skill", current_files, False))
          describe.append(return_role_prompts(role, "describe", current_files, False))
          current_files = new
      res.append({"repo":project, "description":describe, "skills":skills})
    return pd.DataFrame(res)
#  collate(firstJs, "Machine Learning Engineer")

  """def truncate(prompt_rec):
    des_index = prompt_rec["description"].find(prompt_rec["cut1"]) + len(prompt_rec["cut1"]) - 1
    ski_index = prompt_rec["skills"].find(prompt_rec["cut2"]) + len(prompt_rec["cut2"]) - 1
    return {'description': prompt_rec["description"][des_index:], 'skills':prompt_rec["skills"][ski_index:]}

  prompts = df.apply(func, axis=1, result_type="expand")
  prompts.columns = ("repo",  "prompt1", "prompt2", "cut1", "cut2")
  prompts = Dataset.from_pandas(prompts)
  descriptions = gen_pipeline(prompts["prompt1"], max_new_tokens=100)
  skills = gen_pipeline(prompts["prompt2"], max_new_tokens=50)
  res = Dataset.from_dict({"repo": prompts["repo"], "description":descriptions, "skills":skills, "cut1":prompts["cut1"], "cut2":prompts["cut2"]})
  res = res.map(lambda x: {'description': x['description'][0]['generated_text'],
                    'skills': x['skills'][0]['generated_text']})
  res = res.map(truncate)
  return res"""
  collate(df, role)
